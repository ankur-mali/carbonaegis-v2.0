import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor

def generate_pdf_report(organization_name, report_year, prepared_by, report_date, 
                        include_charts=True, include_methodology=True, include_recommendations=True):
    """
    Generate a PDF report based on the emissions data.
    
    Args:
        organization_name (str): The name of the organization
        report_year (int): The reporting year
        prepared_by (str): Name of the person who prepared the report
        report_date (datetime): Date of the report
        include_charts (bool): Whether to include charts in the report
        include_methodology (bool): Whether to include methodology section
        include_recommendations (bool): Whether to include recommendations section
        
    Returns:
        bytes: The PDF report as bytes
    """
    # Create a buffer to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        leading=22,
        alignment=1,  # Center
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceAfter=8
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading3'],
        fontSize=12,
        leading=14,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    # Build the story (content elements)
    story = []
    
    # Title
    story.append(Paragraph(f"Emission Baseline Report", title_style))
    story.append(Paragraph(f"{organization_name}", subtitle_style))
    story.append(Spacer(1, 12))
    
    # Report information
    info_data = [
        ["Reporting Period:", f"January 1, {report_year} - December 31, {report_year}"],
        ["Prepared By:", prepared_by],
        ["Date:", report_date.strftime('%B %d, %Y')]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 24))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", subtitle_style))
    summary_text = f"""
    This report provides a comprehensive overview of greenhouse gas (GHG) emissions for {organization_name} 
    during the {report_year} reporting period. All calculations follow the GHG Protocol Corporate Standard methodology.
    """
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 12))
    
    # Key Findings
    story.append(Paragraph("Key Findings", heading_style))
    
    # Total emissions
    story.append(Paragraph(f"Total GHG Emissions: {st.session_state.total_emissions:.2f} tCO₂e", normal_style))
    story.append(Spacer(1, 6))
    
    # Emissions by scope
    scope_data = [
        ["Emissions by Scope", "tCO₂e", "Percentage"],
        ["Scope 1 (Direct)", f"{st.session_state.scope1_total:.2f}", f"{(st.session_state.scope1_total / st.session_state.total_emissions * 100):.1f}%"],
        ["Scope 2 (Indirect Energy)", f"{st.session_state.scope2_total:.2f}", f"{(st.session_state.scope2_total / st.session_state.total_emissions * 100):.1f}%"],
        ["Scope 3 (Other Indirect)", f"{st.session_state.scope3_total:.2f}", f"{(st.session_state.scope3_total / st.session_state.total_emissions * 100):.1f}%"],
        ["Total", f"{st.session_state.total_emissions:.2f}", "100.0%"]
    ]
    
    scope_table = Table(scope_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    scope_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f0f0f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(scope_table)
    story.append(Spacer(1, 24))
    
    # Charts
    if include_charts:
        story.append(Paragraph("Emissions Overview", subtitle_style))
        
        # Pie chart of emissions by scope (reportlab doesn't create actual charts in this code)
        # In real implementation, we would create charts using reportlab's charting capabilities
        story.append(Paragraph("Note: The actual report would include pie charts and bar charts visualizing the emissions data.", normal_style))
        story.append(Spacer(1, 24))
    
    # Detailed Results
    story.append(Paragraph("Detailed Emissions Results", subtitle_style))
    
    # Build emissions data table
    emissions_table_data = [["Scope", "Emission Source", "Emissions (tCO₂e)", "% of Total"]]
    
    # Add Scope 1 emissions
    if hasattr(st.session_state, 'emissions_data') and 'scope1' in st.session_state.emissions_data:
        for source, value in st.session_state.emissions_data['scope1'].items():
            percentage = (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
            emissions_table_data.append([
                "Scope 1", 
                source.replace("_", " ").title(), 
                f"{value:.2f}", 
                f"{percentage:.1f}%"
            ])
    
    # Add Scope 2 emissions
    if hasattr(st.session_state, 'emissions_data') and 'scope2' in st.session_state.emissions_data:
        for source, value in st.session_state.emissions_data['scope2'].items():
            percentage = (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
            emissions_table_data.append([
                "Scope 2", 
                source.replace("_", " ").title(), 
                f"{value:.2f}", 
                f"{percentage:.1f}%"
            ])
    
    # Add Scope 3 emissions
    if hasattr(st.session_state, 'emissions_data') and 'scope3' in st.session_state.emissions_data:
        for source, value in st.session_state.emissions_data['scope3'].items():
            percentage = (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
            emissions_table_data.append([
                "Scope 3", 
                source.replace("_", " ").title(), 
                f"{value:.2f}", 
                f"{percentage:.1f}%"
            ])
    
    # Create table
    emissions_table = Table(emissions_table_data, colWidths=[1*inch, 3*inch, 1*inch, 1*inch])
    emissions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(emissions_table)
    story.append(Spacer(1, 24))
    
    # Input Data
    story.append(Paragraph("Activity Data Used", subtitle_style))
    
    # Build input data table
    input_data_rows = []
    
    # Scope 1 inputs
    input_data_rows.append(["Scope", "Source", "Activity Data", "Unit"])
    
    # Add Scope 1 inputs
    input_data_rows.append(["Scope 1", "Natural Gas", f"{st.session_state.get('natural_gas', 0)}", "m³"])
    input_data_rows.append(["Scope 1", "Stationary Diesel", f"{st.session_state.get('diesel_stationary', 0)}", "liters"])
    input_data_rows.append(["Scope 1", "Gasoline", f"{st.session_state.get('gasoline', 0)}", "liters"])
    input_data_rows.append(["Scope 1", "Mobile Diesel", f"{st.session_state.get('diesel_mobile', 0)}", "liters"])
    input_data_rows.append(["Scope 1", f"Refrigerant ({st.session_state.get('refrigerant_type', 'N/A')})", f"{st.session_state.get('refrigerant_amount', 0)}", "kg"])
    
    # Add Scope 2 inputs
    input_data_rows.append(["Scope 2", "Electricity", f"{st.session_state.get('electricity', 0)}", "kWh"])
    input_data_rows.append(["Scope 2", "Grid Region", f"{st.session_state.get('grid_region', 'N/A')}", ""])
    input_data_rows.append(["Scope 2", "Purchased Steam", f"{st.session_state.get('purchased_steam', 0)}", "MJ"])
    input_data_rows.append(["Scope 2", "Purchased Heat", f"{st.session_state.get('purchased_heat', 0)}", "MJ"])
    
    # Add Scope 3 inputs
    input_data_rows.append(["Scope 3", "Short-haul Air Travel", f"{st.session_state.get('air_travel_short', 0)}", "passenger-km"])
    input_data_rows.append(["Scope 3", "Long-haul Air Travel", f"{st.session_state.get('air_travel_long', 0)}", "passenger-km"])
    input_data_rows.append(["Scope 3", "Hotel Stays", f"{st.session_state.get('hotel_stays', 0)}", "room-nights"])
    input_data_rows.append(["Scope 3", "Rental Car", f"{st.session_state.get('rental_car', 0)}", "km"])
    input_data_rows.append(["Scope 3", "Car Commuting", f"{st.session_state.get('car_commute', 0)}", "passenger-km"])
    input_data_rows.append(["Scope 3", "Public Transit", f"{st.session_state.get('public_transit', 0)}", "passenger-km"])
    input_data_rows.append(["Scope 3", "Landfill Waste", f"{st.session_state.get('landfill_waste', 0)}", "kg"])
    input_data_rows.append(["Scope 3", "Recycled Waste", f"{st.session_state.get('recycled_waste', 0)}", "kg"])
    input_data_rows.append(["Scope 3", "Paper Consumption", f"{st.session_state.get('paper_consumption', 0)}", "kg"])
    input_data_rows.append(["Scope 3", "Water Consumption", f"{st.session_state.get('water_consumption', 0)}", "m³"])
    
    # Create table
    input_table = Table(input_data_rows, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (0, 5), HexColor('#f0f8ff')),  # Scope 1 background
        ('BACKGROUND', (0, 6), (0, 9), HexColor('#f0fff0')),  # Scope 2 background
        ('BACKGROUND', (0, 10), (0, -1), HexColor('#fff0f5')),  # Scope 3 background
    ]))
    
    story.append(input_table)
    story.append(Spacer(1, 24))
    
    # Methodology section
    if include_methodology:
        story.append(Paragraph("Calculation Methodology", subtitle_style))
        
        methodology_text = """
        This GHG emissions inventory follows the Greenhouse Gas Protocol Corporate Standard, which provides 
        requirements and guidance for companies and organizations preparing a GHG emissions inventory.
        
        The emission factors used in the calculations are sourced from internationally recognized databases 
        and are specific to each emission source and activity.
        """
        
        story.append(Paragraph(methodology_text, normal_style))
        story.append(Spacer(1, 12))
        
        # Emission factors table
        story.append(Paragraph("Emission Factors Used", heading_style))
        
        # Too many emission factors to include all, so we'll just show a few examples
        ef_data = [
            ["Category", "Source", "Emission Factor", "Unit"],
            ["Scope 1", "Natural Gas", "0.00205", "tCO₂e/m³"],
            ["Scope 1", "Diesel (stationary)", "0.00270", "tCO₂e/liter"],
            ["Scope 2", "Electricity (US avg)", "0.000416", "tCO₂e/kWh"],
            ["Scope 3", "Air Travel (short haul)", "0.000156", "tCO₂e/passenger-km"]
        ]
        
        ef_table = Table(ef_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        ef_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E8B57')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(ef_table)
        story.append(Spacer(1, 24))
    
    # Recommendations section
    if include_recommendations:
        story.append(Paragraph("Emission Reduction Recommendations", subtitle_style))
        
        recommendations_text = f"""
        Based on the emissions profile of {organization_name}, the following recommendations are provided 
        to reduce GHG emissions:
        """
        
        story.append(Paragraph(recommendations_text, normal_style))
        story.append(Spacer(1, 6))
        
        # Scope 1 recommendations
        story.append(Paragraph("Scope 1 Reduction Strategies:", heading_style))
        scope1_rec = """
        • Optimize heating systems to reduce natural gas consumption
        • Regular maintenance of equipment to ensure optimal performance
        • Consider transitioning to electric or hybrid vehicles
        • Implement a vehicle maintenance program to improve fuel efficiency
        • Regular leak detection and repair for refrigeration systems
        """
        story.append(Paragraph(scope1_rec, normal_style))
        story.append(Spacer(1, 6))
        
        # Scope 2 recommendations
        story.append(Paragraph("Scope 2 Reduction Strategies:", heading_style))
        scope2_rec = """
        • Energy-efficient lighting (LED)
        • Optimized HVAC systems
        • On-site renewable energy generation (solar panels)
        • Purchase of renewable energy credits (RECs)
        """
        story.append(Paragraph(scope2_rec, normal_style))
        story.append(Spacer(1, 6))
        
        # Scope 3 recommendations
        story.append(Paragraph("Scope 3 Reduction Strategies:", heading_style))
        scope3_rec = """
        • Implement a sustainable travel policy
        • Utilize virtual meeting technologies
        • Encourage carpooling and public transportation
        • Implement a comprehensive recycling program
        • Reduce paper usage through digitalization
        """
        story.append(Paragraph(scope3_rec, normal_style))
        story.append(Spacer(1, 24))
    
    # Framework Guidance Section
    if 'framework_recommendations' in st.session_state and st.session_state.framework_recommendations:
        story.append(Paragraph("Disclosure Framework Guidance", subtitle_style))
        
        framework_text = "Based on your organization profile, the following sustainability reporting frameworks are recommended:"
        story.append(Paragraph(framework_text, normal_style))
        story.append(Spacer(1, 6))
        
        # Primary Frameworks
        if st.session_state.framework_recommendations.get('primary'):
            story.append(Paragraph("Primary Recommended Frameworks:", heading_style))
            primary_frameworks = ', '.join(st.session_state.framework_recommendations.get('primary', []))
            story.append(Paragraph(f"• {primary_frameworks}", normal_style))
            story.append(Spacer(1, 6))
        
        # Secondary Frameworks
        if st.session_state.framework_recommendations.get('secondary'):
            story.append(Paragraph("Additional Recommended Frameworks:", heading_style))
            secondary_frameworks = ', '.join(st.session_state.framework_recommendations.get('secondary', []))
            story.append(Paragraph(f"• {secondary_frameworks}", normal_style))
            
        story.append(Spacer(1, 6))
        
        framework_explanation = """
        Using the appropriate reporting framework ensures compliance with relevant regulations and 
        standardizes your sustainability disclosures. For more detailed guidance on framework requirements, 
        please refer to the Framework Finder tool in the Carbon Aegis platform.
        """
        story.append(Paragraph(framework_explanation, normal_style))
        story.append(Spacer(1, 24))
    
    # Footer
    footer_text = f"Generated by GHG Emissions Calculator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', fontSize=8, alignment=1)))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF from the buffer
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def generate_excel_report(organization_name, report_year, prepared_by, report_date):
    """
    Generate an Excel report based on the emissions data.
    
    Args:
        organization_name (str): The name of the organization
        report_year (int): The reporting year
        prepared_by (str): Name of the person who prepared the report
        report_date (datetime): Date of the report
        
    Returns:
        bytes: The Excel report as bytes
    """
    # Create a buffer to store the Excel file
    buffer = io.BytesIO()
    
    # Create a pandas Excel writer
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Create summary sheet
        summary_data = {
            'Organization': [organization_name],
            'Reporting Year': [report_year],
            'Prepared By': [prepared_by],
            'Report Date': [report_date.strftime('%Y-%m-%d')],
            'Total Emissions (tCO₂e)': [st.session_state.total_emissions],
            'Scope 1 Emissions (tCO₂e)': [st.session_state.scope1_total],
            'Scope 2 Emissions (tCO₂e)': [st.session_state.scope2_total],
            'Scope 3 Emissions (tCO₂e)': [st.session_state.scope3_total]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create detailed emissions sheet
        emissions_data = {
            'Scope': [],
            'Emission Source': [],
            'Emissions (tCO₂e)': [],
            'Percentage of Total': []
        }
        
        # Add Scope 1 emissions
        if hasattr(st.session_state, 'emissions_data') and 'scope1' in st.session_state.emissions_data:
            for source, value in st.session_state.emissions_data['scope1'].items():
                emissions_data['Scope'].append('Scope 1')
                emissions_data['Emission Source'].append(source.replace('_', ' ').title())
                emissions_data['Emissions (tCO₂e)'].append(value)
                emissions_data['Percentage of Total'].append(
                    (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
                )
        
        # Add Scope 2 emissions
        if hasattr(st.session_state, 'emissions_data') and 'scope2' in st.session_state.emissions_data:
            for source, value in st.session_state.emissions_data['scope2'].items():
                emissions_data['Scope'].append('Scope 2')
                emissions_data['Emission Source'].append(source.replace('_', ' ').title())
                emissions_data['Emissions (tCO₂e)'].append(value)
                emissions_data['Percentage of Total'].append(
                    (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
                )
        
        # Add Scope 3 emissions
        if hasattr(st.session_state, 'emissions_data') and 'scope3' in st.session_state.emissions_data:
            for source, value in st.session_state.emissions_data['scope3'].items():
                emissions_data['Scope'].append('Scope 3')
                emissions_data['Emission Source'].append(source.replace('_', ' ').title())
                emissions_data['Emissions (tCO₂e)'].append(value)
                emissions_data['Percentage of Total'].append(
                    (value / st.session_state.total_emissions * 100) if st.session_state.total_emissions > 0 else 0
                )
        
        # Add totals
        emissions_data['Scope'].append('Total')
        emissions_data['Emission Source'].append('')
        emissions_data['Emissions (tCO₂e)'].append(st.session_state.total_emissions)
        emissions_data['Percentage of Total'].append(100)
        
        emissions_df = pd.DataFrame(emissions_data)
        emissions_df.to_excel(writer, sheet_name='Emissions Detail', index=False)
        
        # Create input data sheet
        input_data = {
            'Scope': [],
            'Source': [],
            'Activity Data': [],
            'Unit': []
        }
        
        # Add Scope 1 inputs
        input_data['Scope'].append('Scope 1')
        input_data['Source'].append('Natural Gas')
        input_data['Activity Data'].append(st.session_state.get('natural_gas', 0))
        input_data['Unit'].append('m³')
        
        input_data['Scope'].append('Scope 1')
        input_data['Source'].append('Diesel (stationary)')
        input_data['Activity Data'].append(st.session_state.get('diesel_stationary', 0))
        input_data['Unit'].append('liters')
        
        input_data['Scope'].append('Scope 1')
        input_data['Source'].append('Gasoline')
        input_data['Activity Data'].append(st.session_state.get('gasoline', 0))
        input_data['Unit'].append('liters')
        
        input_data['Scope'].append('Scope 1')
        input_data['Source'].append('Diesel (mobile)')
        input_data['Activity Data'].append(st.session_state.get('diesel_mobile', 0))
        input_data['Unit'].append('liters')
        
        input_data['Scope'].append('Scope 1')
        input_data['Source'].append(f"Refrigerant ({st.session_state.get('refrigerant_type', 'N/A')})")
        input_data['Activity Data'].append(st.session_state.get('refrigerant_amount', 0))
        input_data['Unit'].append('kg')
        
        # Add Scope 2 inputs
        input_data['Scope'].append('Scope 2')
        input_data['Source'].append('Electricity')
        input_data['Activity Data'].append(st.session_state.get('electricity', 0))
        input_data['Unit'].append('kWh')
        
        input_data['Scope'].append('Scope 2')
        input_data['Source'].append('Grid Region')
        input_data['Activity Data'].append(st.session_state.get('grid_region', 'N/A'))
        input_data['Unit'].append('')
        
        input_data['Scope'].append('Scope 2')
        input_data['Source'].append('Purchased Steam')
        input_data['Activity Data'].append(st.session_state.get('purchased_steam', 0))
        input_data['Unit'].append('MJ')
        
        input_data['Scope'].append('Scope 2')
        input_data['Source'].append('Purchased Heat')
        input_data['Activity Data'].append(st.session_state.get('purchased_heat', 0))
        input_data['Unit'].append('MJ')
        
        # Add Scope 3 inputs
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Short-haul Air Travel')
        input_data['Activity Data'].append(st.session_state.get('air_travel_short', 0))
        input_data['Unit'].append('passenger-km')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Long-haul Air Travel')
        input_data['Activity Data'].append(st.session_state.get('air_travel_long', 0))
        input_data['Unit'].append('passenger-km')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Hotel Stays')
        input_data['Activity Data'].append(st.session_state.get('hotel_stays', 0))
        input_data['Unit'].append('room-nights')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Rental Car')
        input_data['Activity Data'].append(st.session_state.get('rental_car', 0))
        input_data['Unit'].append('km')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Car Commuting')
        input_data['Activity Data'].append(st.session_state.get('car_commute', 0))
        input_data['Unit'].append('passenger-km')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Public Transit')
        input_data['Activity Data'].append(st.session_state.get('public_transit', 0))
        input_data['Unit'].append('passenger-km')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Landfill Waste')
        input_data['Activity Data'].append(st.session_state.get('landfill_waste', 0))
        input_data['Unit'].append('kg')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Recycled Waste')
        input_data['Activity Data'].append(st.session_state.get('recycled_waste', 0))
        input_data['Unit'].append('kg')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Paper Consumption')
        input_data['Activity Data'].append(st.session_state.get('paper_consumption', 0))
        input_data['Unit'].append('kg')
        
        input_data['Scope'].append('Scope 3')
        input_data['Source'].append('Water Consumption')
        input_data['Activity Data'].append(st.session_state.get('water_consumption', 0))
        input_data['Unit'].append('m³')
        
        input_df = pd.DataFrame(input_data)
        input_df.to_excel(writer, sheet_name='Activity Data', index=False)
        
        # Create methodology sheet
        methodology_data = {
            'Category': ['Overview', 'Standards', 'Scope 1', 'Scope 2', 'Scope 3'],
            'Description': [
                'This emissions inventory follows standard GHG accounting methodologies.',
                'Greenhouse Gas Protocol Corporate Standard',
                'Direct emissions from owned or controlled sources',
                'Indirect emissions from purchased electricity, steam, heating, and cooling',
                'All other indirect emissions in a company\'s value chain'
            ]
        }
        
        methodology_df = pd.DataFrame(methodology_data)
        methodology_df.to_excel(writer, sheet_name='Methodology', index=False)
        
        # Create emission factors sheet
        ef_data = {
            'Category': [],
            'Source': [],
            'Emission Factor': [],
            'Unit': []
        }
        
        # Scope 1 emission factors
        ef_data['Category'].append('Scope 1')
        ef_data['Source'].append('Natural Gas')
        ef_data['Emission Factor'].append(0.00205)
        ef_data['Unit'].append('tCO₂e/m³')
        
        ef_data['Category'].append('Scope 1')
        ef_data['Source'].append('Diesel (stationary)')
        ef_data['Emission Factor'].append(0.00270)
        ef_data['Unit'].append('tCO₂e/liter')
        
        ef_data['Category'].append('Scope 1')
        ef_data['Source'].append('Gasoline')
        ef_data['Emission Factor'].append(0.00233)
        ef_data['Unit'].append('tCO₂e/liter')
        
        ef_data['Category'].append('Scope 1')
        ef_data['Source'].append('Diesel (mobile)')
        ef_data['Emission Factor'].append(0.00267)
        ef_data['Unit'].append('tCO₂e/liter')
        
        # Scope 2 emission factors
        ef_data['Category'].append('Scope 2')
        ef_data['Source'].append('Electricity (US avg)')
        ef_data['Emission Factor'].append(0.000416)
        ef_data['Unit'].append('tCO₂e/kWh')
        
        ef_data['Category'].append('Scope 2')
        ef_data['Source'].append('Purchased Steam')
        ef_data['Emission Factor'].append(0.00009)
        ef_data['Unit'].append('tCO₂e/MJ')
        
        # Scope 3 emission factors
        ef_data['Category'].append('Scope 3')
        ef_data['Source'].append('Air Travel (short haul)')
        ef_data['Emission Factor'].append(0.000156)
        ef_data['Unit'].append('tCO₂e/passenger-km')
        
        ef_data['Category'].append('Scope 3')
        ef_data['Source'].append('Air Travel (long haul)')
        ef_data['Emission Factor'].append(0.000139)
        ef_data['Unit'].append('tCO₂e/passenger-km')
        
        ef_df = pd.DataFrame(ef_data)
        ef_df.to_excel(writer, sheet_name='Emission Factors', index=False)
        
        # Recommendations sheet
        recommendations_data = {
            'Scope': ['Scope 1', 'Scope 1', 'Scope 2', 'Scope 2', 'Scope 3', 'Scope 3'],
            'Recommendation': [
                'Optimize heating systems to reduce natural gas consumption',
                'Consider transitioning to electric or hybrid vehicles',
                'Energy-efficient lighting (LED)',
                'On-site renewable energy generation (solar panels)',
                'Implement a sustainable travel policy',
                'Implement a comprehensive recycling program'
            ]
        }
        
        recommendations_df = pd.DataFrame(recommendations_data)
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
    
    # Get the Excel file from the buffer
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    buffer.close()
    
    return excel_bytes
