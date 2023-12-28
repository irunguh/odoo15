from odoo import fields,_,models,api

class DeclineClaimWizard(models.TransientModel):
    _name = 'decline.claim.wizard'

    name = fields.Text(string='Decline Reasons', required=True)


    def decline_and_email_customer(self):
        claim = self.env['claim.details'].browse(self._context.get('active_ids', []))
        if claim:
           claim.update({"state": "reject", "note_field": self.name})