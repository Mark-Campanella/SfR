import pandas as pd
import re

def clean(df:pd.DataFrame):

    def clean_brackets(text):
        # Is it list-like?
        if isinstance(text, list):
            # if so make it a str and fix it
            return '\n'.join([str(item).replace('[','').replace(']','') for item in text])
        elif isinstance(text, float): return text #well not much can be done with numeric objects
        else:
            # If it is not numeric and it is not a list, the it can be adjusted
            return text.replace('[','').replace(']','')
        
    def clean_kg(text):
        #If is float, nothing to be done
        if isinstance(text, float): return text
        else:
            #remove Kg from word
            return text.replace(',','.').replace('Kg','').replace('kg','') 
        
    def correct_dim_basket(text):
        #If is float, nothing to be done
        if isinstance(text, float): return text
        else:
            #remove string and make it us patterned
            text = text.replace(',','.').replace('cm','').replace('mm','')
            return param_dim_basket(text)
          
    def param_dim_basket(text):
        '''
        If it is not a float yet, make it a float.
        \nIf number//10 is bigger then 9.9999 then this was in mm and needs adjustments.
        \nElse, just return the number, it is already in cm 
        '''
        if isinstance(text, float): num = text
        else: num = float(text)
        
        if (num//10) >= 10: return num/10
        else: return num
    
    def rotation_speed(text):
        if isinstance(text,float): return text
        else: return text.replace("rpm", '')
        
    def adjust_dimensions(text):
        if not isinstance(text,str): return text
        # Expressão regular para capturar largura, altura e profundidade
        padrao = r'Largura:\s*([\d.,]+)cm.*?Altura:\s*([\d.,]+)cm.*?Profundidade:\s*([\d.,]+)cm'
        match = re.search(padrao, text)
        if match:
            largura, altura, profundidade = match.groups()
            largura = largura.replace(',', '.')
            altura = altura.replace(',', '.')
            profundidade = profundidade.replace(',', '.')
            text = largura + 'x' + altura + 'x' + profundidade    
            return text
        
    def adjust_dimensions_mm(text):
        if not isinstance(text,str): return text
        new_text = []
        for num in text.split('x'):
            num = float(num)/10
            new_text.append(str(num))
        return 'x'.join(new_text)
    
    def format_dimensions_isolate(row):
        # Verifica e formata a largura
        largura = str(row['Dimensões do produto - Largura']).replace('cm', '').replace(',', '.').strip()
        # Verifica e formata a altura
        altura = str(row['Dimensões do produto - Altura']).replace('cm', '').replace(',', '.').strip()
        # Verifica e formata a profundidade
        profundidade = str(row['Dimensões do produto - Profundidade']).replace('cm', '').replace(',', '.').strip()
        if largura == 'nan': return pd.NA
        # Retorna as dimensões formatadas
        return f"{largura}x{altura}x{profundidade}"
    
    def format_dimensions_with_package_isolate(row):
        # Verifica e formata a largura
        largura = str(row['Dimensões do produto com embalagem - Largura']).replace('cm', '').replace(',', '.').strip()
        # Verifica e formata a altura
        altura = str(row['Dimensões do produto com embalagem - Altura']).replace('cm', '').replace(',', '.').strip()
        # Verifica e formata a profundidade
        profundidade = str(row['Dimensões do produto com embalagem - Profundidade']).replace('cm', '').replace(',', '.').strip()
        if largura == 'nan': return pd.NA
        # Retorna as dimensões formatadas
        return f"{largura}x{altura}x{profundidade}"
            
    def to_lower(text):
        if isinstance(text,str): return text.lower()
        else: return text
        
    #SKUs are not EXPLICIT so I made some things (tries to get from header, fills based on the "Reference", filled based on the "Model Number"), also make it lowercase
    try:
       df["SKU"] = df["SKU"].fillna(df["Referência"])
    except:pass
    try:
       df["SKU"] = df["SKU"].fillna(df["Modelo"])
    except:pass
    try:
        df["SKU"] = df['SKU'].apply(to_lower)
    except:pass
    try:
    # Fill what is repeated, to delete extra columns later
        df['Capacidade de Lavagem'] = df['Capacidade de Lavagem'].fillna(df['Capacidade'])
        df['Tipo de Abertura'] = df['Tipo de Abertura'].fillna(df['Abertura da Máquina'])
    except:pass

    # Adjust Basket Dimension
    try:
        df['Diâmetro do Cesto'] = df["Diâmetro do Cesto"].apply(correct_dim_basket)
    except Exception as e:
        print("Not able to adjust Basket Dimension, error: ",e)
    except:pass

    # Adjust Rotation Speed
    try:
        df['Velocidades de Centrifugação'] = df["Velocidades de Centrifugação"].apply(rotation_speed)
    except Exception as e:
        print("Not able to adjust Rotation Speed, error: ",e)
  
    # Adjust elements with kg 
    try:
        df["Capacidade de Lavagem"] = df["Capacidade de Lavagem"].apply(clean_kg)
        df["Peso do Produto"] = df["Peso do Produto"].fillna(df["Massa Aproximada do Produto"])
        df["Peso do Produto"] = df["Peso do Produto"].apply(clean_kg)
        df["Peso do Produto com Embalagem"] = df["Peso do Produto com Embalagem"].apply(clean_kg)
    except Exception as e:
        print("Not able to adjust elements with kg, error: ",e)
        
    # Adjust More Images
    try:
        df['More Images'] = df['More Images'].apply(clean_brackets)
    except Exception as e:
        print("Not able to adjust More Images format, error: ",e)
    
    # Adjust Dimensions
    try:
        df['Dimensões do Produto'] = df['Dimensões do Produto'].apply(adjust_dimensions)
        df['Dimensões do Produto'] = df['Dimensões do Produto'].fillna(df['Dimensões do Produto (LxAxP em MM)'].apply(adjust_dimensions_mm))
        df['Dimensões do produto 2'] = df.apply(format_dimensions_isolate, axis=1)
        df['Dimensões do Produto'] = df['Dimensões do Produto'].fillna(df['Dimensões do produto 2'])
        
         # split dimensions in width height depth columns 
        df[['largura', 'altura', 'profundidade']] = df['Dimensões do Produto'].str.split('x', expand=True)
        
        try:
            # convert to float just in case
            df['largura'] = df['largura'].astype(float)
            df['altura'] = df['altura'].astype(float)
            df['profundidade'] = df['profundidade'].astype(float)
        except:print("Not able to convert to float")
        
        #get rid of what we don't need
        df = df.drop(columns=['Dimensões do Produto (LxAxP em MM)','Dimensões do produto 2', 'Dimensões do Produto', 'Dimensões do produto - Largura', 'Dimensões do produto - Altura', 'Dimensões do produto - Profundidade'])

    except Exception as e:
        print("Not able to adjust dimensions, error: ",e)
        
    # Adjust Dimensions with packages
    try:
        df['Dimensões do Produto com Embalagem'] = df['Dimensões do Produto com Embalagem'].apply(adjust_dimensions)
        df['Dimensões do Produto com Embalagem 2'] = df.apply(format_dimensions_with_package_isolate, axis=1)
        df['Dimensões do Produto com Embalagem'] = df['Dimensões do Produto com Embalagem'].fillna(df['Dimensões do Produto com Embalagem 2'])
         # split dimensions in width height depth columns 
        df[['largura com embalagem', 'altura com embalagem', 'profundidade com embalagem']] = df['Dimensões do Produto com Embalagem'].str.split('x', expand=True)
        
        try:
            # convert to float just in case
            df['largura com embalagem'] = df['largura com embalagem'].astype(float)
            df['altura com embalagem'] = df['altura com embalagem'].astype(float)
            df['profundidade com embalagem'] = df['profundidade com embalagem'].astype(float)
        except:print("Not able to convert to float")
        
        #get rid of what we don't need
        df = df.drop(columns=['Dimensões do Produto com Embalagem 2', 'Dimensões do Produto com Embalagem', 'Dimensões do produto com embalagem - Largura', 'Dimensões do produto com embalagem - Altura', 'Dimensões do produto com embalagem - Profundidade'])

    except Exception as e:
        print("Not able to adjust dimensions, error: ",e)
    
    
    try:
        df = df.drop(columns=['Capacidade','Marca', 'Abertura da Máquina',"Massa Aproximada do Produto"])
    except:pass
    df_translated = df.copy()
    try:
        #create translator
        # Specify which columns are not going to be translated
        col_ignore = ['Link', 'Price', 'Brand', 'Image', 'Five Star','Review Amount','SKU','More Images','Referência','Modelo']
        # This function adds GOOGLETRANSLATE({x},'auto') in the objects
        def apply_googletranslate(x):
            if pd.isna(x):
                return ''  # If nan shouldn't be translated
            if isinstance(x, (int, float)):
                return x  # If numeric, shouldn't be translated
            return f'=GOOGLETRANSLATE("{x}", "auto")'
        # we will not change the original document
       
        for col in df.columns:
            if col not in col_ignore:#ignore those we don't want to translate
                df_translated[col] = df[col].apply(apply_googletranslate)

        translated_columns = [apply_googletranslate(col) for col in df.columns]
        df_translated.columns = translated_columns
    except Exception as e:
        print("Not able to translate because of: ", e)
    try:   
        dataframes = [df, df_translated]
        
        
        
        #print summary
        print(df.info())
        print("\n\n",df_translated.info())
    except:pass
    return dataframes