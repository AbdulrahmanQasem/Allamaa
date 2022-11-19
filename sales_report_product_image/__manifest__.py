# See LICENSE file for full copyright and licensing details.
{
    # Module information
    "name": "Product Image for Sale",
    "version": "15.0.1.0.1",
    "category": "Sales Management",
    "sequence": "1",
    "summary": """Product Image for Quatation/Sale Reports.""",
    "description": """Product Image for Quatation/Sale Reports.""",
    "license": "LGPL-3",
    # Author
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    # Dependencies
    "depends": ["sale_management", "stock", "sh_so_html_notes", 'base',"mrp"],
    # Views
    "data": [
        "views/sale_product_view.xml", 
        "views/report_saleorder.xml", 
        'views/res_config_settings_view.xml',
        "reports/quotation.xml", 
        "reports/contract.xml", 
        "reports/organizations_report2.xml", 
        "reports/organizations_report3.xml"
    ],
    # Techical
    "installable": True,
    "auto_install": False,
}
