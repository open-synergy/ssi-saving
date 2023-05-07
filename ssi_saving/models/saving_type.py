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

    # Interest related fields
    interest_rate = fields.Float(
        string="Interest Amount",
        company_dependent=True,
    )
    interest_calculation_method = fields.Selection(
        string="Interest Calculation Method",
        selection=[
            ("average", "Average Balance"),
            ("lowest", "Lowest Balance"),
            ("ending", "Ending Balance"),
        ],
        required=True,
        default="average",
    )
    interest_account_id = fields.Many2one(
        string="Interest Account",
        comodel_name="account.account",
        required=True,
    )
    interest_journal_id = fields.Many2one(
        string="Interest Journal",
        comodel_name="account.journal",
        required=True,
    )
    interest_period_type_id = fields.Many2one(
        string="Interest Period Type",
        comodel_name="date.range.type",
        required=True,
    )
    interest_tax_ids = fields.Many2many(
        string="Interest Taxes",
        comodel_name="account.tax",
        required=True,
    )
    interest_cron_id = fields.Many2one(
        string="Interest Cron",
        comodel_name="ir.cron",
        readonly=True,
    )

    def action_create_interest_cron(self):
        for record in self.sudo():
            record._create_interest_cron()

    def action_delete_interest_cron(self):
        for record in self.sudo():
            record._create_delete_cron()

    def _create_interest_cron(self):
        self.ensure_one()

    def _delete_interest_cron(self):
        self.ensure_one()
