import pandas as pd

def merge(df: pd.DataFrame):
    try:
        df_SASVA = pd.read_csv("statics/sasva.csv")
        # Removing duplicates from SAS VA data
        df_SASVA_unique = df_SASVA.drop_duplicates(subset='ProductID', keep='first')

        # Merging
        df_merged = pd.merge(
            df,
            df_SASVA_unique[['ProductID', 'DPLPlatform', 'Comm.Seg.']],
            how='left',  # use 'left' to keep all entries in df
            left_on='SKU',
            right_on='ProductID'
        )
    except Exception as e:
        print("SAS VA data not found! Error: ", e)
        return df

    try:    
        df_launch_year = pd.read_csv("statics/traqline.csv")  # Get traqline SKUmetrix data
        df_launch_year = df_launch_year.rename(columns={'SKU': 'Identifier', 'SKUs Recently Added': 'Year'})
        df_merged = pd.merge(
            df_merged,
            df_launch_year[['Identifier', 'Year']],
            how='left',
            left_on='SKU',
            right_on='Identifier'
        ).drop(columns=['Identifier'])
        df_merged["Launch Year"] = df_merged["Launch Year"].fillna(df_merged["Year"])  # Fill the information gaps
        df_merged = df_merged.drop(columns=['Year'])  # Drop the 'Year' column
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print("Could not merge datasets: ", e)

    # Ordering the columns
    try:
        ideal_columns_order = [
            'DPLPlatform', 'Comm.Seg.', 'Brand', 'SKU', 'Description', 'Washer/Dryer Combo Type',
            'Washer Load Type', 'Product Height', 'Product Width', 'Product Depth', 'Capacity',
            'Washer Capacity', 'Dryer Capacity', 'Price', 'Five Star', 'Review Amount', 'Link',
            'Product Name', 'Drying Type', 'Display Type', 'Washer Tub/Drum Material', 'Washing Mechanism',
            'Maximum Spin Speed', 'Name', 'Image Link', 'More Images Links', 'Videos Links', 'Energy Guide', 'Document 1', 'Document 2',
            'Depth With Door Open', 'Launch Year', 'Steam Function', 'Dryer Heating Source', 'Moisture Sensor',
            'Matching Washer Model Number', 'App Compatible', 'Color Finish', 'Model Number', 'Color',
            'Interior Light(s)', 'Control Type', 'Control Location', 'Drum Material', 'Number Of Drying Cycles',
            'Antimicrobial Protection', 'Out-Of-Balance Detection', 'Internal Water Heater', 'Built-In Water Faucet',
            'Detergent Dispenser Type', 'Estimated Annual Electricity Use', 'Tub/Drum Material', 'Dryer Drum Material',
            'Number of Rinse Temperatures', 'Estimated Annual Electricity Use (Dryer)', 'OBX', 'Drying Cycles',
            'Options and Programs', 'Number of Temperature Settings', 'Matching Washer Type', 'Temperature Settings',
            'Amperage', 'Voltage', 'ENERGY STAR Certified', 'ADA Compliant', 'Manufacturer\'s Warranty - Parts',
            'Manufacturer\'s Warranty - Labor', 'Wireless Connectivity', 'Self-Cleaning Filter',
            'Consortium for Energy Efficiency (CEE) Rating', 'CEE Qualified', 'High-Efficiency', 'Integrated Water Heater',
            'Automatic Temperature Control', 'Bleach Dispenser', 'Fabric Softener Dispenser', 'Pre-Wash Detergent Dispenser',
            'Number of Wash/Rinse Cycles', 'Wash/Rinse Cycles', 'Number of Wash Temperatures', 'Number of Drying Temperatures',
            'Number of Spin Speeds', 'Soil Levels', 'Estimated Annual Electricity Use (Washer)', 'Washer Voltage',
            'Dryer Voltage', 'Height With Door Open', 'Agitator Type', 'UPC', 'Vendor Collection', 'Fingerprint Resistant',
            'Product Safety Certifications and Standards', 'NSF Listed', 'Lint Filter Full Indicator', 'Pedestal Available',
            'Matching Washer Available', 'Compact Design', 'Stacking Kit Included', 'Power Cord Included', 'Child Lock',
            'Vibration Reduction', 'Second Rinse', 'Washer Interior Light', 'Sensor Dry', 'Dryer Interior Light',
            'Dryer Door Style', 'Washer Window', 'Dryer Window', 'Fill Hoses Included', 'Drain Hose Included',
            'Estimated Annual Operating Cost (Washer)', 'Matching Dryer Model Number', 'Height To Control Panel Top',
            'Detergent Form', 'Soft Close Lid', 'Adjustable Leveling Legs', 'Matching Dryer Available',
            'Estimated Annual Operating Cost', 'Wheels/Casters', 'Faucet Adapter Included', 'ANSI Certified', 'AAFA Certified',
            'Drying Rack', 'Window', 'Water Source', 'Dryer Depth With Door Open', 'Stackable', 'Stacking Kit Model Compatibility',
            'Works With', 'Pedestal Model Compatibility', 'Product Weight', 'Delay Start', 'End-Of-Cycle Signal',
            'Time-Remaining Display', 'Reversible Door Hinge', 'Exhaust Vent Location', '4-Way Venting', 'Noise Reduction',
            'Estimated Annual Operating Cost (Dryer)', 'Door Style', 'Propane Conversion Kit Model Compatibility',
            'Propane (LP) Convertible', 'Propane Conversion Kit Included', 'Payment System', 'Total Maximum BTU Rating',
            'Gas Connector Included', 'Commercial Merchandise', 'Unnamed: 123'
        ]
        
        # Get real columns in the DataFrame
        real_columns_order = df_merged.columns.to_list()
        
        # Filter ideal columns to only those present in real columns
        columns_order = [col for col in ideal_columns_order if col in real_columns_order]
        
        # New columns not in the ideal list
        remaining_columns = [col for col in real_columns_order if col not in columns_order]
        
        # Reordering columns
        df_merged = df_merged.reindex(columns=columns_order + remaining_columns)
        
    except Exception as e:
        print("Error in ordering the columns: ", e)
    
    return df_merged
