# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import calendar
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class PosDashboard(models.Model):
    """

    The ProjectDashboard class provides the data to the js when the dashboard is loaded.
        Methods:
            get_tiles_data(self):
                when the page is loaded get the data from different models and transfer to the js file.
                return a dictionary variable.
            get_top_timesheet_employees(model_ids):
               getting data for the timesheet graph.
            get_hours_data(self):
                getting data for the hours table.
            get_task_data(self):
                getting data to project task table
            get_project_task_count(self):
                getting data to project task table
            get_color_code(self):
                getting dynamic color code for the graph
            get_income_this_month(self):
                getting data to profitable graph after month filter apply
            get_income_last_year(self):
                getting data to profitable graph after last year filter apply
            get_income_this_year(self):
                getting data to profitable graph after current year filter apply
            get_details(self):
                getting data for the profatable table

    """
    _inherit = 'project.project'

    @api.model
    def get_tiles_data(self):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting the dashboard view.

        """
        # Get logged user allowed projects per branch
        current_company = self.env.company.ids
        branch_ids = self.env.user.branch_ids.ids
        all_project = self.env['project.project'].search([])
        # project task stages
        project_task_stages_pending = self.env['project.task.type'].search([('is_pending','=',True)])
        project_task_stages_done = self.env['project.task.type'].search([('is_done', '=', True)])
        ## all tasks
        all_tasks_ids_pending = self.env['project.task.type'].search([('is_pending','in',True)])
        all_tasks_ids_done = self.env['project.task.type'].search([('is_done', 'in', True)])
        # all pending tasks
        all_pending_task = self.env['project.task'].search([('stage_id','in',project_task_stages_pending.ids),('branch_id','in',branch_ids)])
        # all done tasks
        all_pending_done = self.env['project.task'].search([('stage_id', 'in', project_task_stages_done.ids),('branch_id','in',branch_ids)])
        # merge 2 lists - https://www.geeksforgeeks.org/python-ways-to-concatenate-two-lists/
        merged_lists = [y for x in [all_tasks_ids_pending.ids,all_tasks_ids_done.ids] for y in x]
        # all tasks in pending or done stage
        all_task = self.env['project.task'].search([('stage_id', 'in', merged_lists),('branch_id','in',branch_ids)])
        #
        analytic_project = self.env['account.analytic.line'].search([])
        # report_project = self.env['project.profitability.report'].search([])
        # to_invoice = sum(report_project.mapped('amount_untaxed_to_invoice'))
        # invoice = sum(report_project.mapped('amount_untaxed_invoiced'))
        # timesheet_cost = sum(report_project.mapped('timesheet_cost'))
        # other_cost = sum(report_project.mapped('expense_cost'))
        # profitability = to_invoice + invoice + timesheet_cost + other_cost
        total_time = sum(analytic_project.mapped('unit_amount'))
        employees = self.env['hr.employee'].search([])

        task = self.env['project.task'].search_read([
            ('sale_order_id', '!=', False)
        ], ['sale_order_id'])
        task_so_ids = [o['sale_order_id'][0] for o in task]
        sale_orders = self.mapped('sale_line_id.order_id') | self.env[
            'sale.order'].browse(task_so_ids)
        sale_list = [rec.id for rec in sale_orders]
        project_stage_ids = self.env['project.project.stage'].search([])
        project_stage_list = []
        for project_stage_id in project_stage_ids:
            total_projects = self.env['project.project'].search_count(
                [('stage_id', '=', project_stage_id.id),
                 ('branch_id','in',branch_ids)])
            project_stage_list.append({
                'name': project_stage_id.name,
                'projects': total_projects,
            })
        return {
            'total_projects': len(all_project),
            'total_tasks': len(all_task),
            'all_pending_tasks': len(all_pending_task),
            'all_pending_done': len(all_pending_done),
            'total_hours': total_time,
            'total_profitability': 0,
            'total_employees': len(employees),
            'total_sale_orders': len(sale_orders),
            'project_stage_list': project_stage_list,
            'sale_list': sale_list
        }

    @api.model
    def get_top_timesheet_employees(self):
        """

        Summery:
            when the page is loaded get the data for the timesheet graph.
        return:
            type:It is a list. This list contain data that affecting the graph of employees.

        """

        query = '''select hr_employee.name as employee,sum(unit_amount) as unit
                    from account_analytic_line
                    inner join hr_employee on hr_employee.id =account_analytic_line.employee_id
                    group by hr_employee.id ORDER 
                    BY unit DESC Limit 10 '''
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()

        unit = []
        for record in top_product:
            unit.append(record.get('unit'))
        employee = []
        for record in top_product:
            employee.append(record.get('employee'))
        final = [unit, employee]

        return final

    @api.model
    def get_details(self):
        """

            Summery:
                when the page is loaded get the data for the profitable table.
            return:
                type:It is a dictionary variable. This dictionary contain data
                that  profitable table.

            """
        query = '''select sum(amount_untaxed_invoiced) as invoiced,
            sum(amount_untaxed_to_invoice) as to_invoice,sum(timesheet_cost) as 
            time_cost,
            sum(expense_cost) as expen_cost,
            sum(margin) as payment_details from project_profitability_report'''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        invoiced = []
        for record in data:
            invoiced.append(record.get('invoiced'))

        to_invoice = []
        for record in data:
            to_invoice.append(record.get('to_invoice'))
            record.get('to_invoice')
        time_cost = []
        for record in data:
            time_cost.append(record.get('time_cost'))

        expen_cost = []
        for record in data:
            expen_cost.append(record.get('expen_cost'))

        payment_details = []
        for record in data:
            payment_details.append(record.get('payment_details'))
        return {
            'invoiced': invoiced,
            'to_invoice': to_invoice,
            'time_cost': time_cost,
            'expen_cost': expen_cost,
            'payment_details': payment_details,
        }

    @api.model
    def get_hours_data(self):
        """

        Summery:
            when the page is loaded get the data for the hours table.
        return:
            type:It is a dictionary variable. This dictionary contain data that  hours table.

        """
        query = '''SELECT sum(unit_amount) as hour_recorded FROM account_analytic_line
        WHERE timesheet_invoice_type='non_billable_project' '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        hour_recorded = []
        for record in data:
            hour_recorded.append(record.get('hour_recorded'))

        query = '''SELECT sum(unit_amount) as hour_recorde FROM account_analytic_line
                WHERE timesheet_invoice_type='billable_time' '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        hour_recorde = []
        for record in data:
            hour_recorde.append(record.get('hour_recorde'))

        query = '''SELECT sum(unit_amount) as billable_fix FROM account_analytic_line
                       WHERE timesheet_invoice_type='billable_fixed' '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        billable_fix = []
        for record in data:
            billable_fix.append(record.get('billable_fix'))

        query = '''SELECT sum(unit_amount) as non_billable FROM account_analytic_line
                               WHERE timesheet_invoice_type='non_billable' '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        non_billable = []
        for record in data:
            non_billable.append(record.get('non_billable'))

        query = '''SELECT sum(unit_amount) as total_hr FROM account_analytic_line
                WHERE timesheet_invoice_type='non_billable_project' or timesheet_invoice_type='billable_time'
                or timesheet_invoice_type='billable_fixed' or timesheet_invoice_type='non_billable' '''
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        total_hr = []
        for record in data:
            total_hr.append(record.get('total_hr'))

        return {
            'hour_recorded': hour_recorded,
            'hour_recorde': hour_recorde,
            'billable_fix': billable_fix,
            'non_billable': non_billable,
            'total_hr': total_hr,
        }

    @api.model
    def get_income_this_year(self):
        """

        Summery:
            when the filter is applied get the data for the profitable graph.
        return:
            type:It is a dictionary variable. This dictionary contain data for  profitable graph.

        """

        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""

        self._cr.execute(('''select sum(margin) as income ,to_char(project_profitability_report.line_date, 'Month') 
                            as month from project_profitability_report where 
                            to_char(DATE(NOW()), 'YY') = to_char(project_profitability_report.line_date, 'YY')
                            %s  group by month ''') % (states_arg))
        record = self._cr.dictfetchall()

        records = []
        for month in month_list:
            last_month_inc = list(
                filter(lambda m: m['month'].strip() == month, record))

            if not last_month_inc:
                records.append({
                    'month': month,
                    'profit': 0.0,
                })

            else:

                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income']
                })
                records.append(last_month_inc[0])

        month = []
        profit = []
        for rec in records:
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'profit': profit,
            'month': month,
        }

    @api.model
    def get_income_last_year(self):
        """

        Summery:
            when the filter is applied get the data for the profitable graph.
        return:
            type:It is a dictionary variable. This dictionary contain data for  profitable graph.

        """
        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""
        self._cr.execute(('''select sum(margin) as income ,to_char(project_profitability_report.line_date, 'Month')  
                        as month from project_profitability_report where
                        Extract(year FROM project_profitability_report.line_date) = Extract(year FROM DATE(NOW())) -1
                                    %s group by month ''') % (states_arg))
        record = self._cr.dictfetchall()

        records = []
        for month in month_list:
            last_month_inc = list(
                filter(lambda m: m['month'].strip() == month, record))
            if not last_month_inc:
                records.append({
                    'month': month,
                    'profit': 0.0,

                })

            else:

                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income']
                })
                records.append(last_month_inc[0])

        month = []
        profit = []
        for rec in records:
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {

            'month': month,
            'profit': profit,
        }

    @api.model
    def get_income_this_month(self):
        """

        Summery:
            when the filter is applied get the data for the profitable graph.
        return:
            type:It is a dictionary variable. This dictionary contain data for  profitable graph.

        """
        states_arg = ""
        day_list = []
        now = datetime.now()
        day = calendar.monthrange(now.year, now.month)[1]
        for x in range(1, day + 1):
            day_list.append(x)
        self._cr.execute(('''select sum(margin) as income ,cast(to_char(project_profitability_report.line_date, 'DD')
                                as int) as date from project_profitability_report where   
                                Extract(month FROM project_profitability_report.line_date) = Extract(month FROM DATE(NOW()))  
                                AND Extract(YEAR FROM project_profitability_report.line_date) = Extract(YEAR FROM DATE(NOW()))
                                %s  group by date  ''') % (states_arg))

        record = self._cr.dictfetchall()

        records = []
        for date in day_list:
            last_month_inc = list(filter(lambda m: m['date'] == date, record))
            if not last_month_inc:
                records.append({
                    'date': date,
                    'income': 0.0,
                    'profit': 0.0
                })

            else:

                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income']
                })
                records.append(last_month_inc[0])
        date = []
        profit = []
        for rec in records:
            date.append(rec['date'])
            profit.append(rec['profit'])
        return {
            'date': date,
            'profit': profit

        }

    @api.model
    def get_task_data(self):
        branch_ids = self.env.user.branch_ids.ids
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting project task table.

        """
        len_tuple = tuple(branch_ids)
        if len(len_tuple) == 1:
            sql_query = ('''select project_task.name as task_name,pro.name as project_name from project_task
                         Inner join project_project as pro on project_task.project_id = pro.id 
                         WHERE pro.branch_id = {0} ORDER BY project_name ASC'''.format(branch_ids[0]))
        else:
            sql_query = ('''select project_task.name as task_name,pro.name as project_name from project_task
                         Inner join project_project as pro on project_task.project_id = pro.id 
                         WHERE pro.branch_id in {0} ORDER BY project_name ASC'''.format(len_tuple))
        try:
            self._cr.execute(sql_query)
            data = self._cr.fetchall()
            project_name = []
            for rec in data:
                b = list(rec)
                project_name.append(b)
            return {
                'project': project_name
            }
        except Exception as e:
            _logger.info(e)
    @api.model
    def get_project_task_completion_data(self):
        branch_ids = self.env.user.branch_ids.ids
        len_tuple = tuple(branch_ids)
        if len(len_tuple) == 1:
            sql_query = (''' SELECT
              project_name,
              ROUND ( (SUM(pending_tasks) / SUM(total_tasks)) * 100 ) as percentage_complete
            FROM (
              SELECT
                p.name as project_name,
                CASE WHEN pty.is_pending THEN COUNT(pt.name) ELSE 0 END as pending_tasks,
                COUNT(pt.name) as total_tasks
              FROM
                project_task pt
                LEFT JOIN project_project p ON p.id = pt.project_id 
                LEFT JOIN project_task_type pty ON pt.stage_id = pty.id
              WHERE
                pty.is_pending = True OR pty.is_done = True AND pt.branch_id = {0}
              GROUP BY
                p.name, pty.is_pending
            ) AS subquery 
            GROUP BY
              project_name;
             '''.format(branch_ids[0]))
        else:
            #print("Debug>>>>>>>>>>>>>>>>>>>>>>>> 2 {0}".format(len_tuple))
            sql_query = (''' SELECT
                          project_name,
                          ROUND ( (SUM(pending_tasks) / SUM(total_tasks)) * 100 ) as percentage_complete
                        FROM (
                          SELECT
                            p.name as project_name,
                            CASE WHEN pty.is_pending THEN COUNT(pt.name) ELSE 0 END as pending_tasks,
                            COUNT(pt.name) as total_tasks
                          FROM
                            project_task pt
                            LEFT JOIN project_project p ON p.id = pt.project_id 
                            LEFT JOIN project_task_type pty ON pt.stage_id = pty.id
                          WHERE
                            pty.is_pending = True OR pty.is_done = True AND p.active = True AND p.branch_id in {0}
                          GROUP BY
                            p.name, pty.is_pending
                        ) AS subquery
                        GROUP BY
                          project_name;
                         '''.format(tuple(branch_ids)))
        self._cr.execute(sql_query)
        data = self._cr.fetchall()
        project_name = []
        for rec in data:
            b = list(rec)
            project_name.append(b)
        return {
            'project': project_name
        }

    @api.model
    def get_project_task_count(self):
        """

        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data for the project task graph.

        """
        project_name = []
        total_task = []
        colors = []
        # project task stages
        branch_ids = self.env.user.branch_ids.ids
        project_task_stages_pending = self.env['project.task.type'].search([('is_pending', '=', True)])
        project_task_stages_done = self.env['project.task.type'].search([('is_done', '=', True)])
        ## all tasks
        all_tasks_ids_pending = self.env['project.task.type'].search([('is_pending', 'in', True)])
        all_tasks_ids_done = self.env['project.task.type'].search([('is_done', 'in', True)])
        # all pending tasks
        all_pending_task = self.env['project.task'].search(
            [('stage_id', 'in', project_task_stages_pending.ids), ('branch_id', 'in', branch_ids)])
        # all done tasks
        all_pending_done = self.env['project.task'].search(
            [('stage_id', 'in', project_task_stages_done.ids), ('branch_id', 'in', branch_ids)])
        # merge 2 lists - https://www.geeksforgeeks.org/python-ways-to-concatenate-two-lists/
        merged_lists = [y for x in [all_tasks_ids_pending.ids, all_tasks_ids_done.ids] for y in x]
        project_ids = self.env['project.project'].search([('branch_id','in',branch_ids)])
        for project_id in project_ids:
            project_name.append(project_id.name)
            task = self.env['project.task'].search_count(
                [('project_id', '=', project_id.id),('stage_id','in',merged_lists)])
            total_task.append(task)
            color_code = self.get_color_code()
            colors.append(color_code)
        return {
            'project': project_name,
            'task': total_task,
            'color': colors
        }

    def get_color_code(self):
        """

        Summery:
            the function is for creating the dynamic color code.
        return:
            type:variable containing color code.

        """
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return color
