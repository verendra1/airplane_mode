import frappe
import pandas as pd
import sys
import re

#     first_row = df.iloc[0].copy()
#     new_df = pd.DataFrame([first_row, first_row], columns=columns)
#     new_df = pd.concat([new_df, df.iloc[1:].reset_index(drop=True)], ignore_index=True)   
#     print(new_df, "----------------------------------------------------------")

@frappe.whitelist()
def data():
    df = pd.read_excel("/home/verendra/Downloads/common_account_numbers_for_replacing_washsss.xlsx")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    grouped = df.groupby('common_account_number')   
    final_dfs = []
    for _, group_df in grouped:
        first_row = group_df.iloc[0].copy()
        df1 = pd.DataFrame([first_row, first_row], columns=group_df.columns)
        df1 = pd.concat([df1, group_df.iloc[1:].reset_index(drop=True)], ignore_index=True)
        final_dfs.append(df1)    
    final_dataframes = []
    for new_df in final_dfs:
        new_data = {
            'common_account_number': new_df['common_account_number'],
            'j104_membership_card_no': [None] + new_df['j104_membership_card_no'].tolist()[1:],
            'j104_char_departure': [None] + new_df['j104_char_departure'].tolist()[1:],
            'j104_full_name': [None] + new_df['j104_full_name'].tolist()[1:],
            'j104_rev_bkt_mem_curr': [None] + new_df['j104_rev_bkt_mem_curr'].tolist()[1:],
            'wash_invoice_account': [new_df['wash_invoice_account'].iloc[0]] + [None] * (len(new_df) - 1),
            'wash_invoice_checkout_date': [new_df['wash_invoice_checkout_date'].iloc[0]] + [None] * (len(new_df) - 1),
            'wash_invoice_stay_revenue': [new_df['wash_invoice_stay_revenue'].iloc[0]] + [None] * (len(new_df) - 1),
            'wash_invoice_member': [new_df['wash_invoice_member'].iloc[0]] + [None] * (len(new_df) - 1),
            'src': [new_df['src'].iloc[0]] + [None] * (len(new_df) - 1),
            'status': [new_df['status'].iloc[0]] + [None] * (len(new_df) - 1),
            'amount_difference': new_df['amount_difference'],
            'category': new_df['category'],
            'period': new_df['period'],
            'hospitality_unit_name': new_df['hospitality_unit_name'],
            'stay_type': [new_df['stay_type'].iloc[0]] + [None] * (len(new_df) - 1),
            'wash_invoice_prop_rate': [new_df['wash_invoice_prop_rate'].iloc[0]] + [None] * (len(new_df) - 1),
            'multi_select': [new_df['multi_select'].iloc[0]] + [None] * (len(new_df) - 1)
        }

        columns = ['common_account_number', 'j104_membership_card_no', 'j104_char_departure', 'j104_full_name',
                   'j104_rev_bkt_mem_curr', 'wash_invoice_account', 'wash_invoice_checkout_date',
                   'wash_invoice_stay_revenue', 'wash_invoice_member', 'src', 'status', 'amount_difference',
                   'category', 'period', 'hospitality_unit_name', 'stay_type', 'wash_invoice_prop_rate',
                   'multi_select']
        
        final_df = pd.DataFrame(new_data, columns=columns)
        final_dataframes.append(final_df)    
    final_result = pd.concat(final_dataframes, ignore_index=True)    
    final_result.to_excel("/home/verendra/Downloads/common123456.xlsx", index=False)   
    return final_result


    # headings=['AGENT_NAME1', 'H_ROWNUM', 'H_RESORT', 'HOLD_ACCODE', 'ACCOUNT_SNAME1', 'ACCOUNT_NAME1', 
    # 'ACCOUNT_NO1', 'CREDIT_LIMIT1', 'H_CONTACT', 'H_PHONE', 'H_FAXCHA', 'H_EMAIL_ADDRESS', 'HOLDAGE1', 
    # 'HOLD_AGE1', 'CP_2', 'HOLD_AGE2', 'HOLD_AGE3', 'HOLD_AGE4', 'HOLD_AGE5', 'HOLD_TOTAL', 'HOLD_AGE6', 'CF_12']

    # values=[['\t43\tBLRSW\t19501\t24 TECH HOTEL PRESTIGE ESTATE PROJECTS L\t24 Tech Hotel Prestige Estate Projects L\t24T0051\t100000\t\t\t\t\t68595.4\t68595.4\t1\t0\t0\t0\t0\t68595.4\t0\t.7413961393283853942'], 
    # ['\t86\tBLRSW\t18250\tAMAZON DEVELOPMENT CENTRE PVT LTD\tAMAZON DEVELOPMENT CENTRE PVT LTD\tAMA0043\t25000000\t\t0\t\tsdsr@amazon.com\t3378930\t3378930\t1\t0\t0\t0\t0\t3378930\t0\t36.52031560514059631'],
    # ['\t62\tBLRSW\t19750\tBAXTER INNOVATIONS\tBaxter Innovations\tBAX0051\t350000\t\t2249484810\t\tasifa_begum@baxter.com\t39778\t39778\t1\t0\t0\t0\t0\t39778\t0\t.4299305147313743226'],
    # ['\t225\tBLRSW\t44251\tDINEOUT( TIMES INTERNET)\tDineout( Times Internet)\tCORTIP0106\t500000\t\t\t\t\t5784.57\t5784.57\t1\t0\t0\t0\t0\t5784.57\t0\t.0625210708833944885'], 
    # ['\t270\tBLRSW\t62752\tEAZYDINER PRIVATE LIMITED\tEAZYDINER PRIVATE LIMITED\tEAZY000235\t125000\t\t\t\t\t10514.48\t10514.48\t1\t0\t0\t0\t0\t10514.48\t0\t.1136431142473915402'], 
    # ['\t251\tBLRSW\t65501\tERNST AND YOUNG LLP\tErnst and Young LLP\tEY0000235\t2000000\t\t\t\t\t892729.1\t892729.1\t1\t0\t0\t0\t0\t892729.1\t0\t9.648838088357296516'], 
    # ['\t223\tBLRSW\t52501\tEY GLOBAL DELIVERY SERVICES INDIA LLP\tEY Global Delivery Services India LLP\tCOREYG178\t7000000\t\t\t\t\t147308.84\t147308.84\t1\t0\t0\t0\t0\t147308.84\t0\t1.592150570810037284'],
    # ['\t94\tBLRSW\t15750\tFOUR POINTS BY SHERATON\tFour Points By Sheraton\tFOU0027\t3000000\t\t8884666841\t\t\t182189.04\t182189.04\t1\t0\t0\t0\t0\t182189.04\t0\t1.969144445311854435'], 
    # ['\t252\tBLRSW\t65502\tHONDA MOTORCYCLE AND\tHonda Motorcycle and\tHOND0023\t2000000\t\t\t\t\t1162708.1\t1162708.1\t1\t0\t0\t0\t0\t1162708.1\t0\t12.56683825017191033'], 
    # ['\t260\tBLRSW\t60003\tINR HOLDINGS(MAAYA)\tINR HOLDINGS(MAAYA)\tINR30035\t100000\t\t\t\t\t9154.44\t9154.44\t1\t0\t0\t0\t0\t9154.44\t0\t.0989434637557816470'], 
    # ['\t61\tBLRSW\t11500\tMAKE MY TRIP INDIA PVT. LTD.\tMake My Trip India Pvt. Ltd.\tMAK008\t600000\t\t\t\tSHAILESH.322@GMAIL.COM\t48498\t48498\t1\t0\t0\t0\t0\t48498\t0\t.5241784429443961964'], 
    # ['\t211\tBLRSW\t48751\tMARRIOTT BONVOY F&B REDEMPTION ACCOUNT\tMarriott Bonvoy F&B Redemption Account\tMBVFB305\t100000\t\t\t\t\t11023.61\t11023.61\t1\t19679.88\t0\t0\t0\t30703.49\t0\t.3318509542900498819'], 
    # ['\t172\tBLRSW\t42751\tNEXUSMALLS WHITEFIELD PVT LTD UNIT OAKWO\tNEXUSMALLS WHITEFIELD PVT LTD UNIT OAKWO\tCORORP150\t350000\t\t\t\tmohammedrafiq.mir@marriott.com\t293413.5\t293413.5\t1\t0\t0\t0\t0\t293413.5\t0\t3.171286064762785957'], 
    # ['\t273\tBLRSW\t60002\tPRESTIGE ESTATES (FALCON LAUNDRY)\tPrestige Estates (Falcon Laundry)\tPRGF3034\t100000\t\t\t\t\t17121.8\t17121.8\t1\t0\t0\t0\t0\t17121.8\t0\t.1850566717061603117'], 
    # ['\t84\tBLRSW\t13000\tPRESTIGE ESTATES PROJECTS LTD\tPrestige Estates Projects Ltd\tPRE009\t12000000\tLalitha\t\t\tmanish.tiwari@sheraton.com\t7642.86\t7642.86\t1\t0\t0\t0\t0\t7642.86\t0\t.0826059312640110502'], 
    # ['\t255\tBLRSW\t58751\tPRESTIGE FAMILY', '.\tPrestige Family', '.\tCORPF205\t100000\t\t\t\t\t65826.3\t65826.3\t1\t0\t0\t0\t0\t65826.3\t0\t.7114670179964268081'], 
    # ['\t168\tBLRSW\t41751\tSONY INDIA SOFTWARE CENTRE PVT LTD\tSony India Software Centre Pvt Ltd\tCORSIS0101\t2200000\t\t9845215468\t\tMuthuraj.Adiga@sony.com\t45155\t45155\t1\t0\t0\t0\t0\t45155\t0\t.4880464677131883840'], 
    # ['\t78\tBLRSW\t10250\tSPG REWARD (MARRIOTT BONVOY)\tSPG Reward (Marriott Bonvoy)\tSPG001\t300000\t\t\t\t\t3114.26\t3114.26\t1\t0\t0\t0\t0\t3114.26\t0\t.0336596964353997134'], 
    # ['\t8\tBLRSW\t21000\tTATA CONSULTANCY SERVICES LIMITED\tTata Consultancy Services Limited\tTCS0056\t1800000\t\t9036024548\t\tanu.antony3@tcs.com\t83550.6\t83550.6\t1\t0\t0\t0\t0\t83550.6\t0\t.9030356595131772206'], 
    # ['\t181\tBLRSW\t56751\tTATA STARBUCKS PVT LTD\tTata Starbucks Pvt Ltd\tCORSBP195\t15000000\t\t\t\t\t2127760.77\t2127760.77\t1\t0\t0\t0\t0\t2127760.77\t0\t22.99736746622065895'], 
    # ['\t176\tBLRSW\t52001\tTLC DIGITECH PRIVATE LIMITED\tTLC Digitech Private Limited\tCORTRM181\t950000\t\t\t\t\t363006.86\t363006.86\t1\t0\t0\t0\t0\t363006.86\t0\t3.923468403912211181'], 
    # ['\t182\tBLRSW\t43001\tZOMATO MEDIA PRIVATE LIMITED\tZomato Media Private Limited\tCORZMP0120\t550000\t\t\t\t\t130854.4\t130854.4\t1\t0\t0\t0\t0\t130854.4\t0\t1.414306891921794664'],
    # ['\t167\tBLRSW\t41502\tZZZ PMS UPI PAY', '', ' 9229\tZZZ PMS UPI Pay', '', ' 9229\tDFTPMSUPI\t\t\t\t\t\t64748.68\t64748.68\t1\t0\t0\t0\t0\t64748.68\t0\t.6998198330880648091'], 
    # ['\t166\tBLRSW\t41501\tZZZ POS UPI','', '', ' 9228\tZZZ POS UPI', '', ' 9228\tDFTUPI\t\t\t\t\t\t73104.28\t73104.28\t1\t0\t0\t0\t0\t73104.28\t0\t.7901292354936526036']]


    # # joined_string = ["".join(row).split('\t') for row in values]

    # joined_string = [' '.join(row).split('\t') for row in values]
    # df=pd.DataFrame(joined_string, columns=headings)
    
    # print(df)
    # df.to_excel("/home/verendra/Downloads/verendra.xlsx")


    # print(joined_string)
    # # list_of_lists = [[string] for string in joined_string]
    # # print(list_of_lists)
    # # data = list(map(lambda x: x[0].split('\t'), list_of_lists))
    # df=pd.DataFrame(joined_string, columns=headings)
    # df.to_excel("/home/verendra/Downloads/verendra.xlsx")
    # print(df)
    # return df

#, None, header_format)

# Your remaining code...





































