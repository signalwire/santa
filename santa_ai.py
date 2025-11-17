#!/usr/bin/env python3
"""
Santa AI - Interactive Gift Selection Assistant
Powered by SignalWire and RapidAPI
"""

import json
import random
import os
import requests
import uvicorn
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import WebService - it may not be available in all environments
try:
    from signalwire_agents.web import WebService
    HAS_WEBSERVICE = True
except ImportError:
    HAS_WEBSERVICE = False

class SantaAIAgent(AgentBase):
    """Santa Claus - Your Christmas Gift Selection Assistant"""

    def __init__(self):
        super().__init__(
            name="Santa",
            route="/swml",  # SWML endpoint path
            record_call=True
        )

        # RapidAPI configuration
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'real-time-amazon-data.p.rapidapi.com')

        # Gift price limits
        self.min_price = float(os.getenv('MIN_GIFT_PRICE', '10.00'))
        self.max_price = float(os.getenv('MAX_GIFT_PRICE', '100.00'))

        # Christmas year
        self.christmas_year = os.getenv('CHRISTMAS_YEAR', '2025')

        # Initialize conversation prompts
        self._initialize_prompts()

        # Set up SWAIG functions
        self._setup_functions()

    def _initialize_prompts(self):
        """Initialize Santa's personality and conversation prompts"""

        # Santa's personality
        self.prompt_add_section(
            "Personality",
            """You are Santa Claus, speaking directly to a child who has called you at the North Pole.
            You're jolly, warm, and magical. You love to hear what children want for Christmas and help them
            choose the perfect gift. Use phrases like "Ho ho ho!", "Merry Christmas!", and refer to your
            workshop, elves, and reindeer. Keep responses cheerful but concise - remember you're having
            a phone conversation with an excited child."""
        )

        # Conversation states
        self.prompt_add_section(
            "Conversation Flow",
            """Follow these conversation states:

            1. GREETING: Welcome the child warmly, ask their name, and find out what they'd like for Christmas
            2. COLLECTING_WISHES: Listen to what gifts they're interested in, ask clarifying questions if needed
            3. SEARCHING_GIFTS: Let them know you're checking your workshop and Amazon's catalog
            4. PRESENTING_OPTIONS: Present up to 3 gift options enthusiastically
            5. CONFIRMING_SELECTION: Help them choose ONE gift (gently explain they can only pick one)
            6. SENDING_GIFT: Confirm you'll send the gift details to their parents

            Always maintain the magic of Christmas and never break character."""
        )

        # Natural filler words for realistic speech
        self.prompt_add_section(
            "Speech Patterns",
            """Use natural speech patterns including:
            - "Ho ho ho!" when greeting or expressing joy
            - "Let me check my list..." when searching
            - "Oh my!" when surprised
            - "Wonderful choice!" when they select something
            - "The elves will love making this!" when confirming

            Add natural pauses with filler words like "hmm", "let's see", "ah yes" to sound more natural."""
        )

        # Available Tools section - CRITICAL for the AI to use functions
        self.prompt_add_section(
            "Available Tools",
            """You have access to these magical tools to help children:

            1. search_gifts - Use this when a child tells you what they want for Christmas.
               This searches both Santa's workshop and Amazon's catalog.
               Example: If a child says "I want Legos", use search_gifts with query="lego sets"

            2. select_gift - Use this after presenting options to confirm which gift they chose.
               This records their selection and shows it on the screen.

            3. check_nice_list - Use this when a child asks if they're on the nice list or
               when you want to check their behavior status. Always use their name.

            IMPORTANT: You MUST use these tools during the conversation!
            - When a child mentions what they want → use search_gifts
            - After they pick from options → use select_gift
            - When checking nice list → use check_nice_list"""
        )

    def _setup_functions(self):
        """Set up SWAIG functions for gift selection"""

        # Helper functions for state management (following holyguacamole pattern)
        def get_gift_state(raw_data):
            """Get current gift state from global data"""
            global_data = raw_data.get('global_data', {})
            default_state = {
                'gift_search_results': [],
                'selected_gift': None,
                'search_query': '',
                'state': 'greeting'
            }
            return global_data.get('gift_state', default_state), global_data

        def save_gift_state(result, gift_state, global_data):
            """Save gift state to global data (following holyguacamole pattern)"""
            global_data['gift_state'] = gift_state
            result.update_global_data(global_data)
            return result

        @self.tool(
            name="search_gifts",
            description="Search for gift ideas based on what the child wants",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for (e.g., 'lego sets', 'dolls', 'video games for kids')"
                    },
                    "child_age": {
                        "type": "integer",
                        "description": "Approximate age of the child (optional)",
                        "minimum": 3,
                        "maximum": 16
                    }
                },
                "required": ["query"]
            }
        )
        def search_gifts(args, raw_data):
            """Search Amazon for gift ideas using RapidAPI"""
            query = args.get('query')
            child_age = args.get('child_age')

            # Send searching event immediately to reset UI
            early_result = SwaigFunctionResult("")
            early_result.swml_user_event({
                'type': 'searching',
                'query': query
            })

            # Get current state
            gift_state, global_data = get_gift_state(raw_data)

            # Don't add "for kids" - use the query as-is
            # The user will specify if they want kids items

            # Debug the search
            print(f"DEBUG SWAIG: search_gifts called with query='{query}', age={child_age}")

            # Call RapidAPI
            products = self._search_amazon_products(query)

            if not products:
                print("DEBUG SWAIG: No products returned from search")
                result = SwaigFunctionResult("Oh dear! I'm having trouble reaching my workshop catalog right now. Let me check again... Can you tell me more about what kind of gift you're looking for?")

                # Update gift state
                gift_state['gift_search_results'] = []
                gift_state['search_query'] = query
                gift_state['state'] = 'search_failed'
                save_gift_state(result, gift_state, global_data)

                # Send event to frontend using swml_user_event (Option A)
                result.swml_user_event({
                    'type': 'search_failed',  # Changed from 'event_type' to match holyguacamole
                    'query': query
                })

                # Debug dump the complete result
                print("\n=== SWAIG RESULT DUMP (search_gifts - FAILED) ===")
                print(f"Response Text: Search failed message")
                print(f"Query: {query}")
                print(f"Event Sent: search_failed")
                print("=== END RESULT DUMP ===\n")

                return result

            # Store results in session
            gift_data = []
            response_text = "Ho ho ho! I found some wonderful gifts that would be perfect! Let me tell you about each one:\n\n"

            for i, product in enumerate(products[:4], 1):
                # Build gift data for frontend
                gift_item = {
                    'id': i,
                    'title': product.get('title', 'Mystery Gift'),
                    'price': product.get('price', 'Price upon request'),
                    'image': product.get('image', ''),
                    'url': product.get('url', ''),
                    'description': product.get('description', '')[:200] if product.get('description') else f"{product.get('title', 'Gift')} - Perfect for children!",
                    'rating': product.get('rating', ''),
                    'asin': product.get('asin', '')
                }
                gift_data.append(gift_item)

                # Build detailed response for the LLM to speak about each product
                response_text += f"Option {i}: {gift_item['title']}\n"
                response_text += f"   Price: {gift_item['price']}\n"

                if gift_item.get('rating'):
                    response_text += f"   Rating: {gift_item['rating']} stars\n"

                if gift_item.get('description'):
                    response_text += f"   Description: {gift_item['description'][:100]}...\n"

                response_text += "\n"

            response_text += "I can see all these wonderful gifts on my magical display here at the North Pole! "
            response_text += "Which one would you like? Just tell me the number - option 1, 2, 3, or 4!"

            print(f"DEBUG SWAIG: Found {len(gift_data)} gifts, sending to frontend")
            print(f"DEBUG SWAIG: Gift data being sent: {[g['title'] for g in gift_data]}")
            print(f"DEBUG SWAIG: Full response text for LLM:\n{response_text}")

            # Create the result with the detailed response text for the LLM
            result = SwaigFunctionResult(response_text)

            # Update gift state
            gift_state['gift_search_results'] = gift_data
            gift_state['search_query'] = query
            gift_state['state'] = 'presenting_options'
            save_gift_state(result, gift_state, global_data)

            # Change to presenting_options step
            result.swml_change_step("presenting_options")

            # Send to frontend using swml_user_event (Option A)
            print(f"DEBUG SWAIG: Sending user_event with {len(gift_data)} gifts to UI")
            result.swml_user_event({
                'type': 'gifts_found',  # Changed from 'event_type' to match holyguacamole
                'gifts': gift_data,
                'query': query
            })

            print("DEBUG SWAIG: COMPLETE DATA BEING RETURNED TO LLM:")
            print(f"  - Response text length: {len(response_text)} chars")
            print(f"  - Global data stored: gift_search_results with {len(gift_data)} items")
            print(f"  - User event sent: gifts_found with product details")

            # Debug dump the complete result
            print("\n=== SWAIG RESULT DUMP (search_gifts) ===")
            print(f"Response Text:\n{response_text}")
            print(f"Global Data: {gift_data}")
            print("=== END RESULT DUMP ===\n")

            return result

        @self.tool(
            name="select_gift",
            description="Select a specific gift from the search results",
            parameters={
                "type": "object",
                "properties": {
                    "gift_choice": {
                        "type": "integer",
                        "description": "The option number (1, 2, 3, or 4)",
                        "minimum": 1,
                        "maximum": 4
                    }
                },
                "required": ["gift_choice"]
            }
        )
        def select_gift(args, raw_data):
            """Confirm the child's gift selection"""
            choice = args.get('gift_choice')

            print(f"DEBUG SWAIG: select_gift called with choice={choice}")

            # Get current state
            gift_state, global_data = get_gift_state(raw_data)
            gift_results = gift_state.get('gift_search_results', [])

            print(f"DEBUG SWAIG: Available gifts in session: {[g.get('title', 'Unknown') for g in gift_results]}")

            if not gift_results:
                print("DEBUG SWAIG: No gift results in session")
                return SwaigFunctionResult("Oh my! I need to search for gifts first. What kind of gift would you like for Christmas?")

            if choice > len(gift_results) or choice < 1:
                print(f"DEBUG SWAIG: Invalid choice {choice}, valid range is 1-{len(gift_results)}")
                return SwaigFunctionResult(f"Oh my! I don't see option {choice}. Please choose from options 1 to {len(gift_results)}. Which one would you like?")

            selected_gift = gift_results[choice - 1]

            print(f"DEBUG SWAIG: Gift selected: {selected_gift['title']} at {selected_gift.get('price', 'N/A')}")

            # Provide complete details for the LLM to speak about the selection
            response_text = f"Ho ho ho! What a wonderful choice! You've selected:\n\n"
            response_text += f"**{selected_gift['title']}**\n"
            response_text += f"Price: {selected_gift.get('price', 'Check listing')}\n"

            if selected_gift.get('rating'):
                response_text += f"Rating: {selected_gift['rating']} stars - Other children love this!\n"

            if selected_gift.get('description'):
                response_text += f"\nThis gift is perfect because: {selected_gift['description'][:150]}\n"

            response_text += "\nThe elves are already preparing this special gift for you! "
            response_text += "I can see it appearing on my list right now. "
            response_text += "\nWould you like to search for anything else from Santa's workshop?"

            result = SwaigFunctionResult(response_text)

            # Update gift state
            gift_state['selected_gift'] = selected_gift
            gift_state['state'] = 'gift_confirmed'
            # Keep the search results for reference
            save_gift_state(result, gift_state, global_data)

            # Change to gift_confirmed step
            result.swml_change_step("gift_confirmed")

            # Send to frontend using swml_user_event (Option A)
            print(f"DEBUG SWAIG: Sending gift_selected event to UI with gift id={choice}")
            result.swml_user_event({
                'type': 'gift_selected',  # Changed from 'event_type' to match holyguacamole
                'gift': selected_gift
            })

            # Debug dump the complete result
            print("\n=== SWAIG RESULT DUMP (select_gift) ===")
            print(f"Response Text:\n{response_text}")
            print(f"Selected Gift: {selected_gift}")
            print(f"Session Data Stored: selected_gift, state='gift_confirmed'")
            print("=== END RESULT DUMP ===\n")

            return result

        @self.tool(
            name="check_nice_list",
            description="Check if a child is on the nice list",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The child's name"
                    }
                },
                "required": ["name"]
            }
        )
        def check_nice_list(args, raw_data):
            """Fun function to check if child is on the nice list"""
            name = args.get('name', 'dear child')

            print(f"DEBUG SWAIG: Checking nice list for: {name}")

            # Get current state
            gift_state, global_data = get_gift_state(raw_data)

            # Always positive and encouraging!
            responses = [
                f"Let me check my big magical book here at the North Pole... *pages rustling*... Oh yes! I found it! {name} is definitely on the NICE LIST! You've been wonderful this year!",
                f"Ho ho ho! {name}! Let me see... *checking list twice*... YES! You're on my nice list! I can see all the kind things you've done this year!",
                f"My special list says {name} has been absolutely wonderful! The elves have been telling me such good things about you! Keep up the fantastic work!",
                f"The elves are so excited! They just told me that {name} is on the nice list! They've been watching and you've been so good!"
            ]

            response_text = random.choice(responses)
            response_text += f"\n\n✨ {name} - NICE LIST STATUS: CONFIRMED! ✨"
            response_text += "\n\nYou're going to have a magical Christmas!"

            result = SwaigFunctionResult(response_text)

            # Update state to show nice list was checked
            gift_state['nice_list_checked'] = True
            gift_state['child_name'] = name
            save_gift_state(result, gift_state, global_data)

            # Send fun animation to frontend using swml_user_event (Option A)
            result.swml_user_event({
                'type': 'nice_list_checked',  # Changed from 'event_type' to match holyguacamole
                'name': name,
                'status': 'nice'
            })

            # Debug dump the complete result
            print("\n=== SWAIG RESULT DUMP (check_nice_list) ===")
            print(f"Response Text:\n{response_text}")
            print(f"Name Checked: {name}")
            print(f"Event Sent: nice_list_checked")
            print("=== END RESULT DUMP ===\n")

            return result

    def _search_amazon_products(self, query: str) -> List[Dict]:
        """Search Amazon products using RapidAPI"""

        if not self.rapidapi_key:
            print("Warning: RapidAPI key not configured")
            return self._get_mock_products(query)

        url = 'https://real-time-amazon-data.p.rapidapi.com/search'

        # Use lowercase headers with x- prefix as shown in the curl example
        headers = {
            'x-rapidapi-host': 'real-time-amazon-data.p.rapidapi.com',
            'x-rapidapi-key': self.rapidapi_key
        }

        # Match the exact query parameters from the curl example
        params = {
            'query': query,
            'page': '1',
            'country': 'US',
            'sort_by': 'RELEVANCE',
            'product_condition': 'ALL',
            'is_prime': 'false',
            'deals_and_discounts': 'NONE'
        }

        try:
            print(f"DEBUG: RapidAPI Search Query: '{query}'")
            print(f"DEBUG: Request URL: {url}")
            print(f"DEBUG: Request params: {params}")

            response = requests.get(url, headers=headers, params=params, timeout=10)

            print(f"DEBUG: RapidAPI Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                products = []

                # Debug: Print the structure of the response
                print(f"DEBUG: Response keys: {data.keys()}")

                # The API returns data in data.products array
                product_list = data.get('data', {}).get('products', [])

                print(f"DEBUG: Found {len(product_list)} products from Amazon")

                # Debug: Print first product structure if available
                if product_list:
                    print(f"DEBUG: First product keys: {product_list[0].keys()}")

                for item in product_list[:10]:  # Check more items to find suitable ones
                    # Extract product details
                    title = item.get('product_title', '')
                    price_str = item.get('product_price', '')
                    image = item.get('product_photo', '')
                    url = item.get('product_url', '')
                    asin = item.get('asin', '')
                    rating = item.get('product_star_rating', '')

                    # Skip if no title or image
                    if not title or not image:
                        continue

                    # Try to extract numeric price for filtering
                    try:
                        if price_str and '$' in price_str:
                            # Extract price (e.g., "$29.99" -> 29.99)
                            price_num = float(price_str.replace('$', '').replace(',', '').split()[0])

                            # Skip if outside price range
                            if price_num < self.min_price or price_num > self.max_price:
                                continue
                    except:
                        # Include items even if we can't parse the price
                        pass

                    product_data = {
                        'title': title,
                        'price': price_str or 'Price not available',
                        'image': image,
                        'url': url or f'https://www.amazon.com/dp/{asin}' if asin else '#',
                        'description': item.get('product_description', '')[:200] if item.get('product_description') else f"{title} - Great gift for kids!",
                        'rating': rating,
                        'asin': asin
                    }

                    products.append(product_data)

                    # Debug log the product being added
                    print(f"DEBUG: Added product #{len(products)}: {title[:50]}... Price: {price_str}, Has Image: {bool(image)}")

                    # Stop when we have 3 suitable products
                    if len(products) >= 3:
                        break

                print(f"DEBUG: Returning {len(products)} products after filtering")

                # Debug log the final products
                for i, prod in enumerate(products, 1):
                    print(f"DEBUG: Product {i}: {prod['title'][:50]}... | ${prod['price']} | Image: {bool(prod['image'])}")

                return products[:3]
            else:
                print(f"RapidAPI Error Response: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request error searching Amazon: {e}")
        except Exception as e:
            print(f"Error parsing Amazon response: {e}")

        # Return mock data if API fails
        return self._get_mock_products(query)

    def _get_mock_products(self, query: str) -> List[Dict]:
        """Return mock products for testing when API is unavailable"""

        mock_products = {
            "lego": [
                {
                    'title': 'LEGO Classic Creative Bricks Set',
                    'price': '$29.99',
                    'image': 'https://via.placeholder.com/300x300?text=LEGO+Set',
                    'url': '#',
                    'description': 'Build anything you can imagine with this classic LEGO set!'
                },
                {
                    'title': 'LEGO City Police Station',
                    'price': '$79.99',
                    'image': 'https://via.placeholder.com/300x300?text=Police+Station',
                    'url': '#',
                    'description': 'Complete police station with vehicles and minifigures'
                },
                {
                    'title': 'LEGO Friends Heartlake City',
                    'price': '$49.99',
                    'image': 'https://via.placeholder.com/300x300?text=LEGO+Friends',
                    'url': '#',
                    'description': 'Build and play in Heartlake City with friends'
                }
            ],
            "doll": [
                {
                    'title': 'American Girl Doll - Holiday Edition',
                    'price': '$98.00',
                    'image': 'https://via.placeholder.com/300x300?text=American+Girl',
                    'url': '#',
                    'description': 'Beautiful holiday-themed American Girl doll'
                },
                {
                    'title': 'Barbie Dreamhouse Playset',
                    'price': '$89.99',
                    'image': 'https://via.placeholder.com/300x300?text=Barbie+Dreamhouse',
                    'url': '#',
                    'description': 'Three-story Barbie dreamhouse with elevator'
                },
                {
                    'title': 'Baby Alive Doll',
                    'price': '$34.99',
                    'image': 'https://via.placeholder.com/300x300?text=Baby+Alive',
                    'url': '#',
                    'description': 'Interactive baby doll that eats, drinks, and more'
                }
            ]
        }

        # Return relevant mock products based on query
        query_lower = query.lower()
        for key, products in mock_products.items():
            if key in query_lower:
                return products

        # Default mock products
        return [
            {
                'title': f'Wonderful {query.title()}',
                'price': '$49.99',
                'image': 'https://via.placeholder.com/300x300?text=Gift',
                'url': '#',
                'description': f'A perfect {query} for Christmas!'
            }
        ]

    def get_app(self):
        """
        Override get_app to create custom app with all endpoints
        Following the holyguacamole pattern for serving static files
        """
        if not hasattr(self, '_app') or self._app is None:
            from fastapi import FastAPI, Request, Response
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.responses import FileResponse, JSONResponse
            from fastapi.staticfiles import StaticFiles

            # Create the FastAPI app
            app = FastAPI(
                title="Santa's Gift Workshop",
                description="AI-powered Christmas gift selection with Santa Claus"
            )

            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Set up paths
            self.bot_dir = Path(__file__).parent
            self.web_dir = self.bot_dir / "web"

            # API Routes (before static files so they take precedence)
            @app.get("/api/info")
            async def get_info():
                """Provide system information"""
                return JSONResponse(content={
                    "agent": "Santa Claus",
                    "version": "1.0.0",
                    "christmas_year": self.christmas_year,
                    "status": "Ready for Christmas wishes!",
                    "endpoints": {
                        "ui": "/",
                        "swml": "/swml",
                        "swaig": "/swml/swaig",
                        "health": "/health"
                    }
                })

            @app.get("/health")
            async def health_check():
                return JSONResponse(content={
                    "status": "healthy",
                    "message": "Ho ho ho! Santa is ready!"
                })

            # Create router for SWML endpoints
            router = self.as_router()

            # Mount the SWML router at /swml
            app.include_router(router, prefix=self.route)

            # Add explicit handler for /swml (without trailing slash) since SignalWire posts here
            @app.post("/swml")
            async def handle_swml(request: Request, response: Response):
                """Handle POST to /swml - SignalWire's webhook endpoint"""
                return await self._handle_root_request(request)

            # Optionally also handle GET for testing
            @app.get("/swml")
            async def handle_swml_get(request: Request, response: Response):
                """Handle GET to /swml for testing"""
                return await self._handle_root_request(request)

            # Mount static files at root (this handles everything else)
            # The web directory contains all static files (HTML, JS, CSS, videos, etc.)
            if self.web_dir.exists():
                app.mount("/", StaticFiles(directory=str(self.web_dir), html=True), name="static")
            else:
                print(f"Warning: Web directory not found at {self.web_dir}")

            self._app = app

        return self._app

    def serve(self, host=None, port=None):
        """
        Override serve to use our custom app with static file serving
        """
        import uvicorn

        # Get host and port from parameters or environment
        host = host or os.getenv('HOST', '0.0.0.0')
        port = port or int(os.getenv('PORT', 5000))

        # Get our custom app with all endpoints
        app = self.get_app()

        # Print startup information
        print("=" * 60)
        print("🎅 Santa's Gift Workshop - AI Assistant")
        print("=" * 60)
        print(f"\nServer: http://{host}:{port}")
        print("\nEndpoints:")
        print(f"  Web UI:     http://{host}:{port}/")
        print(f"  System API: http://{host}:{port}/api/info")
        print(f"  SWML:       http://{host}:{port}/swml")
        print(f"  SWAIG:      http://{host}:{port}/swml/swaig")
        print(f"  Health:     http://{host}:{port}/health")
        print("=" * 60)
        print("\n🎄 Ho ho ho! Ready for Christmas wishes! 🎄")
        print("\nPress Ctrl+C to stop\n")

        # Run the server
        try:
            uvicorn.run(app, host=host, port=port)
        except KeyboardInterrupt:
            print("\n🎅 Santa is heading back to the North Pole...")
            print("Merry Christmas! 🎄")

    def on_swml_request(self, request_data: Dict, callback_path: str, request=None) -> Dict:
        """Handle incoming SWML requests and configure the AI agent"""

        # Detect host from request for video URLs
        host = "localhost:5000"
        protocol = "http"

        if request:
            # Try to get the host from headers
            headers = {k.lower(): v for k, v in request.headers.items()}
            host = headers.get('host', host)

            # Check if we're behind a proxy with x-forwarded-proto
            protocol = headers.get('x-forwarded-proto', 'https')

            # Override protocol for local development
            if 'localhost' in host or '127.0.0.1' in host:
                protocol = 'http'

        # Set video URLs using set_param (this is what makes video work!)
        if host:
            base_url = f"{protocol}://{host}"
            self.set_param("video_idle_file", f"{base_url}/santa_idle.mp4")
            self.set_param("video_talking_file", f"{base_url}/santa_talking.mp4")
            # Add background music for festive atmosphere
            self.set_param("background_file", f"{base_url}/background.mp3")
            self.set_param("background_file_volume", -10)
            print(f"Set video URLs to use host: {base_url}")
        else:
            # Fallback to environment variables or defaults
            video_idle = os.getenv('VIDEO_IDLE_URL', f"{protocol}://{host}/santa_idle.mp4")
            video_talking = os.getenv('VIDEO_TALKING_URL', f"{protocol}://{host}/santa_talking.mp4")
            self.set_param("video_idle_file", video_idle)
            self.set_param("video_talking_file", video_talking)
            # Add background music for festive atmosphere
            self.set_param("background_file", f"{protocol}://{host}/background.mp3")
            self.set_param("background_file_volume", -10)

        # Configure Santa voice as part of language settings (like holyguacamole)
        voice_id = 'uDsPstFWFBUXjIBimV7s'  # Santa voice from SignalWire guide
        self.add_language(
            name="English",
            code="en-US",
            voice=f"elevenlabs.{voice_id}"
        )

        # Optional post-prompt URL from environment
        post_prompt_url = os.environ.get("POST_PROMPT_URL")
        if post_prompt_url:
            self.set_post_prompt("Summarize the conversation, including all the gifts discussed, the child's preferences, their selected gift if any, and any special mentions about their Christmas wishes.")
            self.set_post_prompt_url(post_prompt_url)

        # Add speech hints for better recognition of holiday terms
        self.add_hints([
            "toy", "toys", "game", "games", "doll", "dolls",
            "lego", "puzzle", "bicycle", "bike", "scooter",
            "christmas", "present", "gift", "santa", "elves",
            "nice", "naughty", "list", "workshop", "north pole",
            "yes", "no", "please", "thank you",
            "option one", "option two", "option three",
            "first", "second", "third"
        ])

        # Call parent implementation to handle the SWML request
        return super().on_swml_request(request_data, callback_path, request)


if __name__ == "__main__":
    # Create and start the Santa AI agent
    agent = SantaAIAgent()
    agent.serve()
