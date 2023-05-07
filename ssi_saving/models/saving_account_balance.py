# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class SavingAccountBalance(models.Model):
    _name = "saving_account_balance"
    _description = "Saving Account Daily Balance"
    _order = "saving_account_id, date asc, id"

    interest_computation_id = fields.Many2one(
        string="# Saving Account Interest Computation",
        comodel_name="saving_interest_computation",
        ondelete="set null",
    )
    saving_account_id = fields.Many2one(
        string="# Saving Account",
        comodel_name="saving_account",
        ondelete="cascade",
        required=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="saving_account_id.currency_id",
        store=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    balance = fields.Monetary(
        string="Balance",
        currency_field="currency_id",
        required=True,
    )

    def action_compute_next_day_balance(self):
        for record in self.sudo():
            record._compute_next_day_balance()

    def _compute_next_day_balance(self):
        self.ensure_one()
        next_date = fields.Date.add(self.date, days=1)
        self.saving_account_id._compute_daily_balance(next_date)
