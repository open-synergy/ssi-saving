# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class SavingAccount(models.Model):
    _name = "saving_account"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
    ]
    _description = "Saving Account"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_open",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date = fields.Date(
        string="Date Open",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        domain=[
            "|",
            "&",
            ("parent_id", "=", False),
            ("is_company", "=", False),
            ("is_company", "=", True),
        ],
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="saving_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="type_id.currency_id",
    )
    interest = fields.Float(
        string="Interest (p.a)",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_group_id = fields.Many2one(
        string="Analytic Account Group",
        comodel_name="account.analytic.group",
        required=True,
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        readonly=True,
    )
    transaction_ids = fields.One2many(
        string="Transactions",
        comodel_name="account.analytic.line",
        related="analytic_account_id.line_ids",
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )

    @api.depends(
        "transaction_ids",
        "transaction_ids.amount",
    )
    def _compute_total(self):
        for record in self:
            result = 0.0
            for detail in record.transaction_ids:
                result += detail.amount
            record.amount_total = result

    @api.model
    def _get_policy_field(self):
        res = super(SavingAccount, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "open_ok",
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
        "type_id",
    )
    def onchange_analytic_account_group_id(self):
        self.analytic_account_group_id = False
        if self.type_id:
            self.analytic_account_group_id = self.type_id.analytic_account_group_id

    @ssi_decorator.post_open_action()
    def _create_analytic_account(self):
        if self.analytic_account_id:
            return True
        AA = self.env["account.analytic.account"]
        aa = AA.create(self._prepare_create_analytic_account())
        self.write(
            {
                "analytic_account_id": aa.id,
            }
        )

    def _prepare_create_analytic_account(self):
        return {
            "partner_id": self.partner_id.id,
            "name": self.name,
            "code": self.name,
        }
