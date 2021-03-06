from django.test import TestCase
from server.views.WfModule import wfmodule_detail, wfmodule_render
from rest_framework.test import APIRequestFactory
from rest_framework import status
from server.models import Module, ModuleVersion, WfModule, Workflow, ParameterSpec, ParameterVal
from server.dispatch import test_data_table
from server.tests.utils import *

class WfModuleTests(LoggedInTestCase):

    # Test workflow with modules that implement a simple pipeline on test data
    def setUp(self):
        super(WfModuleTests, self).setUp()  # log in
        self.factory = APIRequestFactory()
        self.workflow1 = add_new_workflow(name='Workflow 1')
        self.workflow2 = add_new_workflow(name='Workflow 2')

        self.module1_version = self.add_new_module_version(name='Module 1', dispatch='testdata', version="1.0")
        self.pspec11 = ParameterSpec.objects.create(module_version=self.module1_version, type=ParameterSpec.NUMBER, def_float=3.14, def_visible=False)
        self.pspec12 = ParameterSpec.objects.create(module_version=self.module1_version, type=ParameterSpec.STRING, def_string='foo')
        self.pspec13 = ParameterSpec.objects.create(module_version=self.module1_version, type=ParameterSpec.CHECKBOX, def_boolean=True)

        self.module2_version = self.add_new_module_version(name='Module 2', dispatch='NOP', version="1.0")
        self.pspec21 = ParameterSpec.objects.create(module_version=self.module2_version, type=ParameterSpec.MENU, def_menu_items='Apple|Banana|Kittens', def_integer=1)

        self.module3_version = self.add_new_module_version(name='Module 3', dispatch='double_M_col', version="1.0")
        self.pspec31 = ParameterSpec.objects.create(module_version=self.module3_version, type=ParameterSpec.BUTTON, def_ui_only=True)

        self.wfmodule1 = self.add_new_wfmodule(self.workflow1, self.module1_version, 1)
        self.wfmodule2 = self.add_new_wfmodule(self.workflow1, self.module2_version, 2)
        self.wfmodule3 = self.add_new_wfmodule(self.workflow1, self.module3_version, 3)
        self.add_new_wfmodule(self.workflow2, self.module1_version, 1)
        self.add_new_wfmodule(self.workflow2, self.module2_version, 2)
        self.add_new_wfmodule(self.workflow2, self.module3_version, 3)


    def add_new_wfmodule(self, workflow_aux, module_aux, order_aux):
        return WfModule.objects.create(workflow=workflow_aux, module_version=module_aux, order=order_aux)

    def add_new_module(self, name, dispatch):
        return Module.objects.create(name=name, dispatch=dispatch)

    def add_new_module_version(self, name, dispatch, version):
        module = self.add_new_module(name=name, dispatch=dispatch)
        module.save()
        module_version = ModuleVersion.objects.create(module = module, source_version_hash = version)
        module_version.save()
        return module_version

    # check that creating a wf_module correctly sets up new ParameterVals w/ defaults from ParameterSpec
    def test_default_parameters(self):
        self.wfmodule1.create_default_parameters()
        pval = ParameterVal.objects.get(parameter_spec=self.pspec11, wf_module=self.wfmodule1)
        self.assertEqual(pval.float, 3.14)
        self.assertEqual(pval.visible, False)
        self.assertEqual(pval.ui_only, False)

        pval = ParameterVal.objects.get(parameter_spec=self.pspec12, wf_module=self.wfmodule1)
        self.assertEqual(pval.string, 'foo')
        self.assertEqual(pval.visible, True)
        self.assertEqual(pval.ui_only, False)
        self.assertEqual(pval.multiline, False) # test correct default

        pval = ParameterVal.objects.get(parameter_spec=self.pspec13, wf_module=self.wfmodule1)
        self.assertEqual(pval.boolean, True)
        self.assertEqual(pval.visible, True)
        self.assertEqual(pval.ui_only, False)

        # Menu should have correct default item
        self.wfmodule2.create_default_parameters()
        pval = ParameterVal.objects.get(parameter_spec=self.pspec21, wf_module=self.wfmodule2)
        self.assertEqual(pval.selected_menu_item_string(), 'Banana')

        # button has no value, so just checking existence here
        self.wfmodule3.create_default_parameters()
        pval = ParameterVal.objects.get(parameter_spec=self.pspec31, wf_module=self.wfmodule3)
        self.assertEqual(pval.visible, True)
        self.assertEqual(pval.ui_only, True)

    # TODO test parameter values returned from this call
    def test_wf_module_detail_get(self):
        # Also tests [Workflow, Module, WfModule].get
        workflow_id = Workflow.objects.get(name='Workflow 1').id
        module_id = Module.objects.get(name='Module 1').id
        module_version = ModuleVersion.objects.get(module = Module.objects.get(name='Module 1'))
        pk_wf_module = WfModule.objects.get(workflow_id=workflow_id,
                                           module_version = module_version).id

        response = self.client.get('/api/wfmodules/%d/' % pk_wf_module)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], pk_wf_module)
        self.assertEqual(response.data['workflow'], workflow_id)
        self.assertEqual(response.data['module_version']['module']['id'], module_id)
        self.assertEqual(response.data['status'], WfModule.READY)
        self.assertEqual(response.data['error_msg'], '')

        response = self.client.get('/api/wfmodules/%d/' % 10000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_wf_module_render_get(self):

        # First module: creates test data
        response = self.client.get('/api/wfmodules/%d/render' % self.wfmodule1.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        test_data_json = table_to_content(test_data_table)
        self.assertEqual(response.content, test_data_json)

        # second module: NOP
        response = self.client.get('/api/wfmodules/%d/render' % self.wfmodule2.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, test_data_json)

        # Third module: doubles M column
        response = self.client.get('/api/wfmodules/%d/render' % self.wfmodule3.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        double_test_data = pd.DataFrame(test_data_table['Class'], test_data_table['M']*2, test_data_table['F'])
        double_test_data = table_to_content(double_test_data)
        self.assertEqual(response.content, double_test_data)


    # can we take one out?
    def test_wf_module_delete(self):
        # add a new one to delete; don't mess with other tests
        wfmodule4 = self.add_new_wfmodule(self.workflow1, self.module1_version, 4)

        response = self.client.delete('/api/wfmodules/%d' % wfmodule4.id)
        self.assertIs(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(WfModule.DoesNotExist):
            WfModule.objects.get(pk=wfmodule4.id)  # must really be gone


    # /input is just a /render on the previous module
    def test_wf_module_input(self):
        # First module: no prior input, should be empty result
        response = self.client.get('/api/wfmodules/%d/input' % self.wfmodule1.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        test_data_json = table_to_content(pd.DataFrame())
        self.assertEqual(response.content, test_data_json)

        # Second module: input should be test data produced by first module
        response = self.client.get('/api/wfmodules/%d/input' % self.wfmodule2.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        test_data_json = table_to_content(test_data_table)
        self.assertEqual(response.content, test_data_json)

        # Third module: should be same as second, as second module is NOP
        response = self.client.get('/api/wfmodules/%d/input' % self.wfmodule3.id)
        self.assertIs(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, test_data_json)


    # test that we can retrieve a stored fetch, going to the db and back
    def test_wf_module_fetch(self):
        text1 = 'just pretend this is json'
        textkey = 'somekey'

        nothing = self.wfmodule1.retrieve_text('somekey')
        self.assertIsNone(nothing)

        self.wfmodule1.store_text(textkey, text1)
        self.wfmodule1.save()
        self.wfmodule1.refresh_from_db()
        text2 = self.wfmodule1.retrieve_text(textkey)
        self.assertEqual(text1, text2)

        # exercise binary storage mode
        bytes1 = b'Let us try this again'
        byteskey = 'newkey'
        self.wfmodule1.store_bytes(byteskey, bytes1)
        self.wfmodule1.save()
        self.wfmodule1.refresh_from_db()
        bytes2 = self.wfmodule1.retrieve_bytes(byteskey)
        self.assertEqual(bytes1, bytes2)

        # ensure data under a different key did not change
        text2 = self.wfmodule1.retrieve_text(textkey)
        self.assertEqual(text1, text2)





