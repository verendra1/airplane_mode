
import tabula 
import pandas as pd
import pdfplumber
import re
import sys
import requests
import os
from tabula.io import read_pdf
import frappe

@frappe.whitelist(allow_guest=True)
def parse_pdf_to_excel(pdf_path):   
        date_pattern = r'\d{2}/\d{2}/\d{2}'
        def remove_nans_and_convert_to_list(row):
            non_nan_values = row.dropna().astype(str)
            return ', '.join(non_nan_values)

        def extract_name_by_removing_date(row):
            date_index = next((i for i, x in enumerate(row) if re.match(date_pattern, str(x))), None)
            if date_index is not None:
                return list(row[:date_index])
            else:
                return list(row)
            
        # Apply join to cells that are lists in the entire DataFrame
        def apply_join(cell):
            if isinstance(cell, list):
                return ' '.join(map(str, cell))
            return cell

        def extract_meeting_date(row):
            row_str = ' '.join(map(str, row))
            matches = re.findall(date_pattern,row_str)
            if len(matches)>=1:
                return matches[0] if matches else " "
            else:
                return " "

        # """for getting page number in which the particular page contains specific string"""
        required_string_in_page="M Bonvoy Events-Catering-SHER"
        pdf = pdfplumber.open(pdf_path)
        extracted_pages = []
        for i, page in enumerate(pdf.pages,1):
            if i > 1:
                data = page.extract_text()
                if required_string_in_page in data:
                    extracted_pages.append(i)
        print(extracted_pages)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

        # Extract tables using Tabula
        tables = []
        for page_num in extracted_pages:
            df = tabula.read_pdf(
                pdf_path,
                pages=page_num,
                multiple_tables=True,
                stream=True,
                guess='stream',
                area=(200.8125, 50.6425, 1000.2825, 706.1025),
                columns=[53.0, 93.0, 170.5, 210.0, 240.0, 310.5, 330.0, 360.0,40  0.0,440.0,470.0]
               
            )
            tables.extend(df)

        # Convert extracted tables to a single DataFrame
        combined_df = pd.concat(tables, ignore_index=True)
        print(combined_df,"||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        df = combined_df.rename(columns={'ACCOUNT': 'ACCOUNT', 'MEMBER NAME': 'MEMBER NAME','DATE':'MEETING DATE','EARNED':'POINTS EARNED',
        'ORG. NAME':'ORG. NAME','NTS':'# NTS','REVENUE':'TOTAL REVENUE','PURCHASED':'ADD.PTS.PURCHASED','SUBTOTAL':'PROP CHG SUBTOTAL','BILLED':'ADD.PTS BILLED','Unnamed: 1':'AMOUNT'})
        if 'Unnamed: 0' in df.columns:
            df.drop(columns=['Unnamed: 0'], inplace=True)

        df.to_excel("/home/verendra/Downloads/Columns_separation.xlsx")
        import sys
        sys.exit()


























        for i in range(0,len(tables)):
            delimiter = ' '
            split_lambda = lambda cell: str(cell).split(delimiter)

            # # Apply the lambda function to each cell in the DataFrame for converting into list
            tables[i] = tables[i].applymap(split_lambda)

            #renaming the column which is located at the last position because we get the amount column at the last in the pdf
            tables[i] = tables[i].rename(columns={tables[i].columns[-1]: 'Amount'})
            tables[i]['Amount'] = tables[i]['Amount'].apply(lambda x: " ".join(x)) 

            tables[i] = tables[i].rename(columns={tables[i].columns[-3]: 'Total Revenue'})
            tables[i]['Total Revenue'] = tables[i]['Total Revenue'].apply(lambda x: " ".join(x))    
            print(tables[i]['Total Revenue'],"////////////////////////////////////////////////")

            tables[i] = tables[i].rename(columns={tables[i].columns[-2]: 'Sub Total'})
            tables[i]['Sub Total'] = tables[i]['Sub Total'].apply(lambda x: " ".join(x))    
            print(tables[i]['Sub Total'],"////////////////////////////////////////////////")       
                 
                    
            # for getting account column
            tables[i]['Account']=tables[i]['ACCOUNTMEMBER NAME'].apply(lambda x: x[0])

            # first removing account number from "ACCOUNTMEMBER NAME" column 
            tables[i]['Member Name']=tables[i]['ACCOUNTMEMBER NAME'].apply(lambda x: x[1:])

            # Now ignoring remaining part after date (including date)
            tables[i]['Member Name'] = tables[i]['Member Name'].apply(lambda row: extract_name_by_removing_date(row))
            tables[i]['Member Name']=tables[i]['Member Name'].apply(lambda a:" ".join(a))
            print(tables[i],"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        
            # now making every cell in dataframe to string
            tables[i] = tables[i].applymap(apply_join)
            
            tables[i]['Meeting Date'] = tables[i].apply(extract_meeting_date, axis=1)

            # Apply the function to every row in the DataFrame
            tables[i]['canextracteverything'] = tables[i].apply(remove_nans_and_convert_to_list, axis=1)

            # adding extra column for getting the remaining data by adding every cell to one cell so that we can remove the already existing data
            tables[i]['canextracteverything'] = tables[i].apply(lambda row: row['canextracteverything'].replace(row['Member Name'], ' '), axis=1)
            tables[i]['canextracteverything'] = tables[i].apply(lambda row: row['canextracteverything'].replace(row['Account'], ' '), axis=1)
            tables[i]['canextracteverything'] = tables[i].apply(lambda row: row['canextracteverything'].replace(row['Meeting Date'], ' '), axis=1)
            tables[i]['canextracteverything'] = tables[i].apply(lambda row: row['canextracteverything'].replace(row['Amount'], ' '), axis=1)

            print(tables[i]['canextracteverything'],"?????????????????????????????????????????????????")
            
            tables[i]['NTS'] = tables[i]['canextracteverything'].apply(lambda lst: lst[-1][-1] if lst and '.' in lst[-1] else lst[-1])                 
            tables[i] = tables[i][["Account","Member Name","Meeting Date","NTS","Amount"]]

            
            
            combined_df = pd.concat(tables, ignore_index=True)
            combined_df = combined_df[combined_df.Account != "nan"]
               
            output_file_path = '/home/verendra/Downloads/janinvoicemarriott.xlsx'
            
            with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
                combined_df.to_excel(writer, sheet_name="Combined_Table", index=False)

            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
# pdf_path = '/home/verendra/Downloads/6.9262056307 Backup Jan 2023.pdf'
# parse_pdf_to_excel(pdf_path)


