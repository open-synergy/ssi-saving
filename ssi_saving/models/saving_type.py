# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class SavingType(models.Model):
    _name = "saving_type"
    _inherit = ["mixin.master_data"]
    _description = "Saving Type"

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
    )
    interest_amount = fields.Float(
        string="Interest Amount",
        company_dependent=True,
    )
    account_id = fields.Many2one(
        string="Saving Account",
        comodel_name="account.account",
        required=True,
    )
    analytic_account_group_id = fields.Many2one(
        string="Analytic Account Group",
        comodel_name="account.analytic.group",
        required=True,
    )
