"""
AI Assistant module for the Carbon Aegis application.
This module integrates with OpenAI to provide AI-powered guidance for sustainability and ESG topics.
"""

import os
import json
from openai import OpenAI

def generate_ai_response(query, context=None):
    """
    Generate an AI response using OpenAI's GPT-4o model.
    
    Args:
        query (str): The user's query
        context (dict, optional): Additional context about the user's organization
        
    Returns:
        str: The generated response
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API key not found. Please add your API key to use AI features."
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Prepare context for the prompt
        context_str = ""
        if context:
            context_str = f"Context about the organization: {json.dumps(context)}\n\n"
        
        # Create system message with expertise on sustainability and ESG
        system_message = """
        You are the Terra ESG AI Assistant, specializing in greenhouse gas emissions calculation, 
        sustainability reporting, ESG frameworks, and environmental regulations. 
        Provide clear, accurate, and actionable guidance on sustainability topics.
        
        Focus areas:
        - GHG emissions calculation methods and standards (GHG Protocol, ISO 14064)
        - Emissions reduction strategies and best practices
        - ESG reporting frameworks (TCFD, GRI, SASB, CDP)
        - Environmental regulations and compliance
        - Science-based targets and net-zero pathways
        
        Always be helpful, concise, and practical in your responses.
        """
        
        # Generate the response
        response = client.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{context_str}User query: {query}"}
            ],
            max_tokens=800
        )
        
        # Return the generated text
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

def analyze_emissions_data(emissions_data):
    """
    Analyze emissions data to provide insights and recommendations.
    
    Args:
        emissions_data (dict): A dictionary containing emissions data by scope
        
    Returns:
        dict: Analysis and recommendations
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OpenAI API key not found"}
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Convert emissions data to string format for the prompt
        emissions_str = json.dumps(emissions_data, indent=2)
        
        # Create system message
        system_message = """
        You are an emissions analysis expert. Analyze the provided GHG emissions data 
        and provide insights and recommendations. Focus on:
        
        1. Key insights about the emissions profile
        2. Comparison to industry benchmarks where possible
        3. Top 3 actionable recommendations for emissions reduction
        4. Areas that may need better data quality
        
        Return your analysis in JSON format with the following structure:
        {
            "insights": [list of key insights],
            "benchmarks": [industry comparisons],
            "recommendations": [actionable recommendations],
            "data_quality": [data quality observations]
        }
        """
        
        # Generate the analysis
        response = client.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Please analyze the following emissions data:\n\n{emissions_str}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        # Parse the JSON response
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    
    except Exception as e:
        return {"error": f"Error analyzing emissions data: {str(e)}"}