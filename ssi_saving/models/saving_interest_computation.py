# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from statistics import mean

from odoo import _, api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class SavingInterestComputation(models.Model):
    _name = "saving_interest_computation"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
    ]
    _description = "Saving Account Interest Computation"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    saving_account_id = fields.Many2one(
        string="# Saving Account",
        comodel_name="saving_account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        related="saving_account_id.partner_id",
        store=True,
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
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    period_type_id = fields.Many2one(
        string="Period Type",
        comodel_name="date.range.type",
        related="saving_account_id.type_id.interest_period_type_id",
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="date.range",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_start = fields.Date(
        string="Date Start",
        related="period_id.date_start",
        store=True,
    )
    date_end = fields.Date(
        string="Date End",
        related="period_id.date_end",
        store=True,
    )
    num_of_days = fields.Integer(
        string="Num of Days",
        compute="_compute_num_of_days",
        store=True,
    )

    interest_rate = fields.Float(
        string="Interest Rate",
        required=True,
        readonly=True,
        related=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    calculation_method = fields.Selection(
        string="Calculation Method",
        selection=[
            ("average", "Average Balance"),
            ("lowest", "Lowest Balance"),
            ("ending", "Ending Balance"),
        ],
        required=True,
        default="average",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    interest_account_id = fields.Many2one(
        string="Interest Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    tax_ids = fields.Many2many(
        string="Interest Taxes",
        comodel_name="account.tax",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    tax_computation_ids = fields.One2many(
        string="Taxes",
        comodel_name="saving_interest_computation_tax",
        inverse_name="interest_computation_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_id = fields.Many2one(
        string="# Accounting Entry",
        comodel_name="account.move",
        readonly=True,
    )
    balance_ids = fields.One2many(
        string="Daily Balance",
        comodel_name="saving_account_balance",
        inverse_name="interest_computation_id",
        readonly=True,
    )
    ending_balance_amount = fields.Monetary(
        string="Ending Balance Amount",
        currency_field="currency_id",
        compute="_compute_balance_amount",
        store=True,
    )
    average_balance_amount = fields.Monetary(
        string="Average Balance Amount",
        currency_field="currency_id",
        compute="_compute_balance_amount",
        store=True,
    )
    lowest_balance_amount = fields.Monetary(
        string="Daily Balance Amount",
        currency_field="currency_id",
        compute="_compute_balance_amount",
        store=True,
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    interest_amount = fields.Monetary(
        string="Interest Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )

    @api.depends(
        "date_start",
        "date_end",
    )
    def _compute_num_of_days(self):
        for record in self:
            result = 0
            if record.date_start and record.date_end:
                result = (record.date_end - record.date_start).days + 1
            record.num_of_days = result

    @api.depends(
        "date_start",
        "date_end",
        "calculation_method",
        "tax_ids",
        "ending_balance_amount",
        "average_balance_amount",
        "lowest_balance_amount",
    )
    def _compute_amount(self):
        for record in self:
            base = interest = tax = 0.0

            if record.calculation_method == "lowest":
                base = record.lowest_balance_amount
            elif record.calculation_method == "average":
                base = record.average_balance_amount
            elif record.calculation_method == "ending":
                base = record.ending_balance_amount

            interest = (
                base
                * ((record.interest_rate / 100.00) * float(record.num_of_days))
                / 365.0
            )

            taxes = record.tax_ids.compute_all(
                interest,
                record.currency_id,
                1.0,
                partner=record.partner_id,
            )
            tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))

            self.base_amount = base
            self.interest_amount = interest
            self.tax_amount = tax

    @api.depends(
        "balance_ids",
        "balance_ids.date",
        "balance_ids.balance",
    )
    def _compute_balance_amount(self):
        for record in self:
            ending = average = lowest = 0.0
            balance_list = record.balance_ids.mapped("balance")
            if len(balance_list) > 0:
                average = mean(balance_list)
                lowest = min(balance_list)

            if len(record.balance_ids) > 0:
                ending = record.balance_ids[-1].balance

            self.ending_balance_amount = ending
            self.average_balance_amount = average
            self.lowest_balance_amount = lowest

    @api.model
    def _get_policy_field(self):
        res = super(SavingInterestComputation, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.onchange(
        "saving_account_id",
    )
    def onchange_calculation_method(self):
        self.calculation_method = False
        if self.saving_account_id:
            self.calculation_method = (
                self.saving_account_id.type_id.interest_calculation_method
            )

    @api.onchange(
        "saving_account_id",
    )
    def onchange_interest_rate(self):
        self.interest_rate = 0.0
        if self.saving_account_id:
            self.interest_rate = self.saving_account_id.type_id.interest_rate

    @api.onchange(
        "saving_account_id",
    )
    def onchange_account_id(self):
        self.account_id = False
        if self.saving_account_id:
            self.account_id = self.saving_account_id.type_id.account_id

    @api.onchange(
        "saving_account_id",
    )
    def onchange_interest_account_id(self):
        self.interest_account_id = False
        if self.saving_account_id:
            self.interest_account_id = (
                self.saving_account_id.type_id.interest_account_id
            )

    @api.onchange(
        "saving_account_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.saving_account_id:
            self.journal_id = self.saving_account_id.type_id.interest_journal_id

    def action_recompute(self):
        self.action_recompute_balance()
        self.action_compute_tax()

    def action_recompute_balance(self):
        for record in self.sudo():
            record._recompute_balance()

    def action_compute_tax(self):
        for record in self:
            record._recompute_tax()

    def _recompute_tax(self):
        self.ensure_one()
        taxes_grouped = self.get_taxes_values()
        self.tax_computation_ids.unlink()
        tax_lines = []
        for tax in taxes_grouped.values():
            tax_lines.append((0, 0, tax))
        self.write({"tax_computation_ids": tax_lines})

    def get_taxes_values(self):
        tax_grouped = {}
        cur = self.currency_id
        round_curr = cur.round
        taxes = self.tax_ids.compute_all(
            self.interest_amount,
            self.currency_id,
            1.0,
            partner=self.partner_id,
        )["taxes"]
        for tax in taxes:
            val = self._prepare_tax_line_vals(tax)
            key = self.get_grouping_key(val)

            if key not in tax_grouped:
                tax_grouped[key] = val
                tax_grouped[key]["base_amount"] = round_curr(val["base_amount"])
            else:
                tax_grouped[key]["tax_amount"] += val["tax_amount"]
                tax_grouped[key]["base_amount"] += round_curr(val["base_amount"])
        return tax_grouped

    def get_grouping_key(self, tax_line):
        self.ensure_one()
        return str(tax_line["tax_id"]) + "-" + str(tax_line["account_id"])

    def _prepare_tax_line_vals(self, tax):
        vals = {
            "interest_computation_id": self.id,
            "tax_id": tax["id"],
            "tax_amount": tax["amount"],
            "base_amount": tax["base"],
            "manual": False,
            "account_id": tax["account_id"],
        }
        return vals

    def _recompute_balance(self):
        self.ensure_one()
        DailyBalance = self.env["saving_account_balance"]
        self.balance_ids.write(
            {
                "interest_computation_id": False,
            }
        )

        criteria = [
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("saving_account_id", "=", self.saving_account_id.id),
        ]
        DailyBalance.search(criteria).write(
            {
                "interest_computation_id": self.id,
            }
        )

    @ssi_decorator.post_done_action()
    def _create_accounting_entry(self):
        self.ensure_one()

        AM = self.env["account.move"]
        move = AM.create(self._prepare_create_accounting_entry())
        move.action_post()
        self.write(
            {
                "move_id": move.id,
            }
        )

    @ssi_decorator.post_cancel_action()
    def _delete_accounting_entry(self):
        self.ensure_one()
        if self.move_id:
            self.move_id.with_context(force_delete=True).unlink()

    def _prepare_create_accounting_entry(self):
        self.ensure_one()
        lines = []
        lines += self._prepare_interest_line()
        lines += self._prepare_saving_line()
        for tax in self.tax_computation_ids:
            lines += tax._prepare_move_line()
        return {
            "name": self.name,
            "journal_id": self.journal_id.id,
            "date": self.date,
            "line_ids": lines,
        }

    def _prepare_interest_line(self):
        self.ensure_one()
        name = "Interest computation for %s duration %s - %s" % (
            self.saving_account_id.name,
            self.date_start,
            self.date_end,
        )
        return [
            (
                0,
                0,
                {
                    "name": _(name),
                    "account_id": self.interest_account_id.id,
                    "debit": self.interest_amount,
                    "partner_id": self.partner_id.id,
                    "currency_id": self.currency_id.id,
                    "analytic_account_id": self.saving_account_id.analytic_account_id.id,
                },
            )
        ]

    def _prepare_saving_line(self):
        self.ensure_one()
        name = "Interest computation for %s duration %s - %s" % (
            self.saving_account_id.name,
            self.date_start,
            self.date_end,
        )
        return [
            (
                0,
                0,
                {
                    "name": _(name),
                    "account_id": self.account_id.id,
                    "credit": self.interest_amount - self.tax_amount,
                    "partner_id": self.partner_id.id,
                    "currency_id": self.currency_id.id,
                    "analytic_account_id": self.saving_account_id.analytic_account_id.id,
                },
            )
        ]
