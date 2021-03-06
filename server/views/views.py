from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from server.models import Module, Workflow, WfModule, ParameterSpec, ParameterVal
from server.serializers import ModuleSerializer, ModuleVersionSerializer
from server.serializers import WorkflowSerializer
from server.serializers import WfModuleSerializer
from server.serializers import ParameterValSerializer
from server.initmodules import init_modules
from pandas import *

# ---- Home Page ----
def index(request):
    return HttpResponse("Hello, world. You're at the workflow index. <a href=\"/admin\">Admin</a>")

# ---- Module ----

# Scaffolding: URL endpoint to trigger module reload from config file
@staff_member_required
def init_modules2(request):
    init_modules()
    return HttpResponse("Loaded module definitions.")

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def module_list(request, format=None):
    if request.method == 'GET':
        workflows = Module.objects.all()
        serializer = ModuleSerializer(workflows, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def module_detail(request, pk, format=None):
    if request.method == 'GET':
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ModuleSerializer(module)
        return Response(serializer.data)

