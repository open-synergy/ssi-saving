# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, fields, models


class SavingInterestComputationTax(models.Model):
    _name = "saving_interest_computation_tax"
    _description = "Saving Account Interest Computation - Tax"

    interest_computation_id = fields.Many2one(
        string="# Saving Account Interest Computation",
        comodel_name="saving_interest_computation",
        required=True,
        ondelete="cascade",
    )
    tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
        required=True,
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="interest_computation_id.currency_id",
        store=True,
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field="currency_id",
        required=True,
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        currency_field="currency_id",
        required=True,
    )
    manual = fields.Boolean(
        string="Manual",
        default=True,
    )

    def _prepare_move_line(self):
        self.ensure_one()
        interest_computation = self.interest_computation_id
        saving_account = interest_computation.saving_account_id
        name = "Interest computation for %s duration %s - %s" % (
            interest_computation.saving_account_id.name,
            interest_computation.date_start,
            interest_computation.date_end,
        )
        return [
            (
                0,
                0,
                {
                    "name": _(name),
                    "account_id": self.account_id.id,
                    "credit": self.tax_amount,
                    "partner_id": interest_computation.partner_id.id,
                    "currency_id": self.currency_id.id,
                    "analytic_account_id": saving_account.analytic_account_id.id,
                },
            )
        ]
