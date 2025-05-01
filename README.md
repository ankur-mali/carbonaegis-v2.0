# Carbon Aegis

Carbon Aegis is a comprehensive greenhouse gas (GHG) emissions calculator and sustainability platform designed to help organizations track, analyze, and reduce their carbon footprint.

## Features

### CLI Version (Available Now)

The CLI (Command Line Interface) version provides the core functionality without external dependencies:

- **Emissions Calculator**: View and calculate GHG emissions across Scope 1, 2, and 3 categories
- **Excel Processing**: Simulation of Excel file imports for emissions data
- **Framework Finder**: Determine which ESG reporting frameworks apply to your organization
- **AI Assistant**: Simulated AI guidance for sustainability questions and emission reduction strategies

### Web Version (Coming Soon)

The full Streamlit web application will add:

- Interactive visualizations and dashboards
- Excel file uploads and automated data mapping
- Detailed reports with export options
- Team collaboration features
- Enhanced AI assistance powered by OpenAI

## Getting Started

### Requirements

- Python 3.6 or higher

### Running the CLI Version

```bash
python simple_cli.py
```

### Menu Options

1. **Process Excel File (Simulation)**: Demonstrates how Excel files would be processed
2. **View Sample Data**: Shows sample emissions data and calculations by scope
3. **Framework Finder**: Interactive tool to find applicable ESG reporting frameworks
4. **AI Assistant**: Simulated AI guidance for sustainability questions
5. **Exit**: Close the application

## Project Structure

- `simple_cli.py`: Command-line interface version
- `app.py`: Main application code (Streamlit version - in development)
- `pages/`: Individual pages for the Streamlit application
- `utils/`: Utility functions for calculations and AI integration

## Development Status

- ✅ CLI version functional without external dependencies
- ⏳ Streamlit web version in development
- ⏳ Database integration planned
- ⏳ Full AI integration with OpenAI planned

## License

All rights reserved.