import os
import sys
from datetime import datetime

def main():
    print("Carbon Aegis CLI Version")
    print("A simple GHG emissions calculator")
    print("-" * 50)
    
    # Menu
    while True:
        print("\nMain Menu:")
        print("1. Process Excel File (Simulation)")
        print("2. View Sample Data")
        print("3. Framework Finder")
        print("4. AI Assistant (Simulation)")
        print("5. Exit")
        
        try:
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                simulate_excel_processing()
            elif choice == '2':
                view_sample_data()
            elif choice == '3':
                framework_finder()
            elif choice == '4':
                ai_assistant()
            elif choice == '5':
                print("Exiting Carbon Aegis CLI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except EOFError:
            # Handle EOF (e.g., when piping input)
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

def simulate_excel_processing():
    print("\n== Excel File Processing Simulation ==")
    print("In a full implementation, this would allow users to upload and process Excel files.")
    
    print("\nSimulating file processing...")
    print("[Step 1/3] Reading Excel data ✓")
    print("[Step 2/3] Analyzing column mappings ✓")
    print("[Step 3/3] Calculating emissions ✓")
    
    print("\nResults from simulated Excel file:")
    view_sample_data()
    
    input("\nPress Enter to return to the main menu...")

def view_sample_data():
    print("\n== Sample GHG Emissions Data ==")
    print("-" * 30)
    
    # Sample data (no pandas required)
    data = [
        ["Date", "Activity", "Amount", "Unit", "Emission Factor", "Scope"],
        ["2024-01-01", "Electricity", "1000", "kWh", "0.45", "Scope 2"],
        ["2024-01-02", "Natural Gas", "500", "kWh", "0.18", "Scope 1"],
        ["2024-01-03", "Vehicle Fuel", "200", "liters", "2.3", "Scope 1"],
        ["2024-01-04", "Air Travel", "5000", "km", "0.15", "Scope 3"],
        ["2024-01-05", "Waste", "100", "kg", "0.5", "Scope 3"]
    ]
    
    # Print the table
    for row in data:
        print("{:<12} {:<15} {:<10} {:<10} {:<15} {:<10}".format(*row))
    
    # Calculate emissions manually
    total = 0
    print("\nEmissions Calculations:")
    for i in range(1, len(data)):
        amount = float(data[i][2])
        factor = float(data[i][4])
        emissions = amount * factor
        total += emissions
        print(f"  {data[i][1]}: {amount} {data[i][3]} * {factor} = {emissions:.2f} kg CO2e")
    
    print(f"\nTotal Emissions: {total:.2f} kg CO2e")
    
    # Show breakdown by scope
    scope1 = sum(float(data[i][2]) * float(data[i][4]) for i in range(1, len(data)) if data[i][5] == "Scope 1")
    scope2 = sum(float(data[i][2]) * float(data[i][4]) for i in range(1, len(data)) if data[i][5] == "Scope 2")
    scope3 = sum(float(data[i][2]) * float(data[i][4]) for i in range(1, len(data)) if data[i][5] == "Scope 3")
    
    print("\nEmissions by Scope:")
    print(f"  Scope 1: {scope1:.2f} kg CO2e ({scope1/total*100:.1f}%)")
    print(f"  Scope 2: {scope2:.2f} kg CO2e ({scope2/total*100:.1f}%)")
    print(f"  Scope 3: {scope3:.2f} kg CO2e ({scope3/total*100:.1f}%)")
    
def framework_finder():
    print("\n== ESG Framework Finder ==")
    print("This tool helps determine which reporting frameworks apply to your organization.")
    
    try:
        print("\nPlease provide the following information:")
        size = input("Company size (Small/Medium/Large): ").strip().capitalize()
        
        listed_str = input("Is your company publicly listed on a stock exchange? (y/n): ").strip().lower()
        listed = listed_str == 'y' or listed_str == 'yes'
        
        turnover = float(input("Annual turnover in millions of euros: "))
        employees = int(input("Number of employees: "))
        sector = input("Industry sector: ")
        country = input("Country of operation: ")
        
        # Determine frameworks based on inputs
        print("\nAnalyzing applicable frameworks...\n")
        
        frameworks = []
        
        # Simple logic based on input 
        if employees > 500 and turnover > 50:
            frameworks.append("EU Corporate Sustainability Reporting Directive (CSRD)")
        
        if listed:
            frameworks.append("Task Force on Climate-related Financial Disclosures (TCFD)")
        
        if turnover > 100 or employees > 1000:
            frameworks.append("Global Reporting Initiative (GRI)")
            
        if sector.lower() in ["energy", "oil", "gas", "utilities"]:
            frameworks.append("Sustainability Accounting Standards Board (SASB)")
            
        # Display results
        if frameworks:
            print("Based on your information, these frameworks likely apply:")
            for framework in frameworks:
                print(f"- {framework}")
        else:
            print("Based on the information provided, no major reporting frameworks are required.")
            print("However, voluntary reporting is recommended using GRI Standards or the GHG Protocol.")
    
    except ValueError:
        print("Invalid input. Please enter numeric values where required.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    input("\nPress Enter to return to the main menu...")

def ai_assistant():
    print("\n== Carbon Aegis AI Assistant ==")
    print("In the full application, this would connect to an AI model to provide")
    print("sustainability guidance and advice based on your emissions data.")
    
    print("\nSimulation of AI assistance:")
    
    question = input("\nWhat sustainability question would you like to ask? ")
    
    print("\nGenerating response...")
    
    # Simulate response based on common sustainability questions
    if "reduce" in question.lower() and any(x in question.lower() for x in ["carbon", "emissions", "footprint"]):
        print("\nAI Response:")
        print("Based on your emissions data, here are the top 3 areas to focus on for reduction:")
        print("1. Vehicle fuel consumption (25.6% of your emissions)")
        print("2. Electricity usage (25.0% of your emissions)")
        print("3. Air travel (41.7% of your emissions)")
        print("\nFor electricity, consider switching to renewable energy sources which")
        print("could reduce your Scope 2 emissions by up to 100%.")
    
    elif "report" in question.lower() or "compliance" in question.lower() or "framework" in question.lower():
        print("\nAI Response:")
        print("Based on your company profile, you should consider these reporting frameworks:")
        print("- GHG Protocol for emissions accounting")
        print("- Global Reporting Initiative (GRI) for overall sustainability reporting")
        print("- CDP for climate-specific disclosures if you have investors who request it")
    
    else:
        print("\nAI Response:")
        print("Thank you for your question about sustainability. In a complete implementation,")
        print("this would provide specific guidance based on your emissions data and the latest")
        print("research on climate action and sustainability best practices.")
    
    input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()