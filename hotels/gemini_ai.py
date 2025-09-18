import google.generativeai as genai
from django.conf import settings
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def initialize_gemini():
    """Initialize the Gemini AI client with API key from settings."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_trip_plan(destination, duration, activities, companions, start_date, origin_location=None, transportation_mode=None):
    """Generate a personalized trip plan using Gemini AI."""
    model = initialize_gemini()
    
    # Format date for display
    from datetime import datetime, timedelta
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = start + timedelta(days=duration-1)
    end_date = end.strftime('%Y-%m-%d')
    
    # Add travel information to prompt if provided
    travel_info = ""
    if origin_location and transportation_mode:
        travel_info = f"""
        Travel Information:
        - Starting from: {origin_location}
        - Transportation mode: {transportation_mode}
        """
    
    # Create a detailed prompt for Gemini
    prompt = f"""
    Create a personalized {duration}-day trip itinerary for {destination} from {start_date} to {end_date}.
    This is for a {companions} trip focusing on these activities: {activities}.
    
    {travel_info}
    
    Please include:
    1. A brief introduction to {destination} highlighting why it's perfect for this type of trip
    2. A day-by-day itinerary with clear Morning, Afternoon, and Evening sections for each day
    3. At least 3 specific attraction recommendations with brief descriptions
    4. 2-3 restaurant recommendations that match the traveler's interests
    5. 1-2 insider tips that most tourists might not know about
    
    COST ESTIMATION SECTION:
    {f"6. Detailed travel cost from {origin_location} to {destination} via {transportation_mode}, including:" if origin_location and transportation_mode else ""}
       {f"- Ticket prices for {transportation_mode} (round trip)" if origin_location and transportation_mode else ""}
       {f"- Any additional transportation costs (airport transfers, taxis, etc.)" if origin_location and transportation_mode else ""}
    
    7. Estimated daily expenses breakdown:
       - Accommodations (options for budget, mid-range, and luxury)
       - Food (average cost per meal and daily total)
       - Activities and attractions (entrance fees, tours, etc.)
       - Local transportation
       - Miscellaneous expenses
    
    8. Total estimated budget range for the entire trip
    
    Format the response in HTML with the following structure:
    - Use <h1> for the main title
    - Use <h2> for day headers like "Day 1" and section headers
    - Use <h3> for subsections
    - Use <p> for paragraphs
    - Use <ul> or <ol> for lists
    - Each day should have clear Morning, Afternoon, and Evening sections
    - Format restaurant names in bold
    - Prefix insider tips with "Tip: " for easy identification
    - Include a "Cost Estimation" section with detailed breakdown of expenses
    - Use <div class="cost-estimation"> to wrap the cost estimation section
    
    IMPORTANT: Make sure the content is detailed, specific to {destination}, and matches the travel preferences.
    If origin location and transportation mode are provided, include realistic cost estimations for travel between {origin_location} and {destination}.
    """
    
    # Generate content with timeout handling using ThreadPoolExecutor
    def call_api():
        try:
            return model.generate_content(prompt).text
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            raise
    
    # Set a timeout for API call - 40 seconds
    with ThreadPoolExecutor() as executor:
        try:
            future = executor.submit(call_api)
            return future.result(timeout=40)
        except TimeoutError:
            print("Gemini API call timed out after 40 seconds")
            raise TimeoutError("AI service took too long to respond")
        except Exception as e:
            print(f"Error in generate_trip_plan: {str(e)}")
            # If the API fails, provide a fallback response
            raise 