================================
                            
 Prepare by : Dikky Suryadi   
                              
===============================

**#product_request_management**
Repo File Odoo Custom 
All Related included For product_request_management Task-2 Vitraining

Tahapan langkah dari pengerjaan UML diatas
**1. Create the Odoo module:**
        ◦ Create directory baru untuk module, contoh., "product_request_management".
        ◦ Dalam folder directory, create "init.py" file dan di mark sabagai a Python package.
        ◦ Create "manifest.py" to define the module and its dependencies.
**2. Define the models:** 
        ◦ Create  Python file, misal., "models.py," mendefinisikan dari models "product_request" dan "request_detail."
        ◦ Inherit the Odoo base models for "stock.picking" and "purchase.order" to add additional fields and functionalities.
**3. Define the views:** 
        ◦ Create a new directory, yaitu, "views," to store the XML views for the product request and request detail.
        ◦ Create a form view for "product_request" to display its fields and related details.
        ◦ Create a tree view to list multiple product requests.
**4. Create the security rules** (optional):
        ◦ If required, create a new directory,yaitu, "security," to store the security rules for the addon.
        ◦ Define the access rules for specific user groups to access the product request and detail records.
**5. Implement the business logic:**
        ◦ Define any business logic yang dibutuhkan, untuk handling state transitions, computing fields, or performing validations.
**6. Implement the controllers** (optional):
        ◦ Jika ingin memg- add any custom web controllers or API endpoints, create a new directory, yaitu, "controllers."
**7. Implement the menus** (optional):
        ◦ Create a new directory, e.g., "data," to store XML files for menu items and actions.
        ◦ Add menu items to the main Odoo menu to access the product request and purchase order views.
**8. Test the module:**  
        ◦ Install the addon in your Odoo instance and make sure it works as expected.
        ◦ Test all the functionalities, including creating product requests, adding request details, and handling purchase orders.

