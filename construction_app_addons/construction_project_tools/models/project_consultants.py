from odoo import fields, api, _ ,models

#main contractors
class ProjectConsultants(models.Model):

    _name = 'project.consultants'
    _description = 'Project Consultants'


    name = fields.Many2one('hr.employee',string='Consultant',required=True)
    #autofill this
    job_position = fields.Char(string='Job Role')
    note = fields.Char(string='Note')

    project_consultant_id = fields.Many2one('project.project', string='Project Reference', required=True,
                                ondelete='cascade', index=True,
                                copy=False)


# sub contractors list
class ProjectSubcontractors(models.Model):

    _name = 'project.subcontractors'
    _description = 'Project Sub Contractors'


    name = fields.Many2one('hr.employee',string='Consultant',required=True)
    #autofill this
    job_position = fields.Char(string='Task Description')
    note = fields.Char(string='Note')

    project_subcontractor_consultant_id = fields.Many2one('project.project', string='Project Subcontractor Reference', required=True,
                                ondelete='cascade', index=True,
                                copy=False)
