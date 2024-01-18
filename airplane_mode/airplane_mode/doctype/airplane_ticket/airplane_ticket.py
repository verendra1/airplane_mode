# Copyright (c) 2023, Verendra and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random
# class AirplaneTicket(Document):

#     def before_save(self):
#         total_amount = self.flight_price  
#         total_amount += sum(add_on.amount for add_on in self.get("add_ons"))

#         self.total_amount = total_amount




class AirplaneTicket(Document):
    def before_save(self):
        total_amount = int(self.flight_price)  # Assuming self.flight_price is an integer
        unique_elements = []

        for row in self.get("add_ons"):
            if row.item in unique_elements:
                self.add_ons.remove(row)
            else:
                unique_elements.append(row.item)
        total_amount += sum(int(add_on.amount) for add_on in self.get("add_ons"))
        self.total_amount = total_amount
        random_integer = str(random.randint(1, 100)) 
        random_alphabet = random.choice(['A', 'B', 'C', 'D', 'E'])  

        self.seat = f"{random_integer}{random_alphabet}"

        self.seat = f"{random_integer}{random_alphabet}"  
    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw("Airplane ticket can only be submitted if the status is 'Boarded'")
