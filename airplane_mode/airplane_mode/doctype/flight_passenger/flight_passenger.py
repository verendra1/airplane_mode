# Copyright (c) 2023, Verendra and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

class FlightPassenger(Document):
    def before_save(self):
        self.full_name = f"{self.first_name} {self.last_name}"

    # def calculate_total_amount(doc,method):
    #         print(doc.add_ons,'************************')
    #         add_ons_total_amount = sum(add_on.amount for add_on in doc.add_ons)
    #         doc.total_amount = doc.flight_price + add_ons_total_amount
    #         print(add_ons_total_amount,'PPPPPPPPPPPPPPPPPPP')

# i have Airplane Ticket doctype in that the fields are  flight_passenger and total_amount .and in that doctype another child table is there name is add_ons, in that child table amount field is there ,
# using before save method ,if i save the document i need, Total Amount = Flight Price + Sum of amounts of all the add-ons that condition using before save method