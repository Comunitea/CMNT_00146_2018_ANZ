.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Description
=================================

Yes No COnfirmation

Configuration
=============

Description of how to configure

Usage
=====

To use this module, you need to:
#. Description of How to use
--------------------------------
ESTA FUNCION ES COMO SE DEFINE EN EL MODELO QUE QUERAMOS HACER LA CONFIRMACION
@api.multi
def function(self):

    yes_confirmation = self._context.get('yes_confirmation', False)
    if not yes_confirmation:
    ____vals = {'function': 'function()',
    ____'name': TITTLE,
    ____'question': QUESTION}
    ____return self.env['yesno.confirmation'].with_context(self._context).return_wzd(self, vals)
    else:
    ____return_id = self._context.get('return_id') or self.id
    ____ctx = self._context.get('ctx', self._context)
    ____if return_id:
    ________AQUI EL CODIGO ORIGINAL DE LA FUNCION
    ________return LOQUESEA
    _____return False

Contributors
------------
* Comunitea
* Kiko Sánchez <kiko@comunitea.com>

Maintainer
----------

This module is maintained by the Comunitea <http://www.comunitea.comm>.
