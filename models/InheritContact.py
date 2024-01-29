from odoo import models, fields, api, SUPERUSER_ID
import psycopg2
import odoorpc


class ContactsWizard(models.TransientModel):
    _name = 'contact.wizard'
    sql_query = fields.Char(string="sql_query")
    # contact = fields.Many2one('res.partner')

    db_name = fields.Char(string="DB Name", required=True)
    db_user = fields.Char(string="UserName", required=True)
    db_pass = fields.Char(string="Password", required=True)
    db_host = fields.Char(string="Host", required=True)
    db_port = fields.Integer(string="PORT", required=True)

    is_connection = fields.Boolean(default=False, store=True)
    show = fields.Boolean(default=True, store=True)
    partner_id = fields.Integer()

    @staticmethod
    def get_default_values():
        return {
            'db_host': 'localhost',
            'db_port': 5432,
            'db_name': 'testdbcopy',
            'db_user': 'odoo',
            'db_pass': 'odoo16',
        }

    def test_connection(self):
        flag = False
        self.partner_id = self.env.context.get('default_partner_id')
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass,
            )
            if conn:
                flag = True
                self.is_connection = True
                self.show = False

        except psycopg2.Error as e:
            error_message = f"Error: {e}"
            raise Warning(error_message)

        finally:
            if conn:
                conn.close()

        return {
            'name': 'Export Contact',
            'type': 'ir.actions.act_window',
            'res_model': 'contact.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('multi_db.multi_db_wizard_form_view').id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_partner_id': self.partner_id},
        }
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'target': 'new',
        #     'params': {
        #         'message': 'Connection Successful' if flag else 'Connection Failed',
        #         'type': 'success' if flag else 'danger',
        #         'next': {
        #
        #             'type': 'ir.actions.act_window',
        #             'res_model': 'contact.wizard',
        #             'view_mode': 'form',
        #             'view_id': self.env.ref('multi_db.multi_db_wizard_form_view_ex').id,
        #             'target': 'new',
        #             'res_id': self.id,
        #         }
        #     }
        # }

    # def action_check(self):
    #     self.is_connection = True
    #     return {
    #         'name': 'Export Contact',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'contact.wizard',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('multi_db.multi_db_wizard_form_view').id,
    #         'target': 'new',
    #         'res_id': self.id,
    #         # 'context': {'default_partner_id': self.id},
    #     }

    def export_data(self):
        partner_id = self.env.context.get('default_partner_id')
        partner = self.env['res.partner'].browse(partner_id)
        vals_list = {'name': partner.name}
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass,
            )
            cr = conn.cursor()
            pg_q = f"""INSERT INTO res_partner(name,email,phone) 
                        VALUES('{partner.name}','{partner.email}','{partner.phone}')"""
            cr.execute(pg_q)
            conn.commit()

        except psycopg2.Error as e:
            error_message = f"Error: {e}"
            raise Warning(error_message)

        finally:
            if conn:
                conn.close()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'target': 'new',
            'params': {
                'message': 'Executed',
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
        return {'type': 'ir.actions.act_window_close'}


class InheritContact(models.Model):
    _inherit = 'res.partner'

    def action_open_wizard(self):
        wizard = self.env['contact.wizard'].create(ContactsWizard.get_default_values())
        return {
            'name': 'Enter DB details',
            'type': 'ir.actions.act_window',
            'res_model': 'contact.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('multi_db.multi_db_wizard_form_view').id,
            'target': 'new',
            'res_id': wizard.id,
            'context': {'default_partner_id': self.id},
        }

