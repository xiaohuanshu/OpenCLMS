from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse
from user.models import Role
from rbac.models import Resourcejurisdiction, Roletoresourcejurisdiction
import json


def jurisdiction_setup(request):
    if request.META['REQUEST_METHOD'] == 'POST':
        rolename = request.GET.get('role', default=None)
        role = Role.objects.get(name=rolename)
        Roletoresourcejurisdiction.objects.filter(role=role).delete()
        newrj = []
        for l in request.POST.getlist('checked[]'):
            newrj.append(
                Roletoresourcejurisdiction(role=role, resourcejurisdiction=Resourcejurisdiction.objects.get(id=l)))
        Roletoresourcejurisdiction.objects.bulk_create(newrj)
        return HttpResponse('{error:0}', content_type="application/json")
    else:
        roledata = Role.objects.all()
        mdata = {}
        mdata['roledata'] = roledata
        rolename = request.GET.get('role', default=None)

        if rolename:
            role = Role.objects.get(name=rolename)
            alreadyjurisdiction = list(role.resourcejurisdiction.values_list('id', flat=True))

            def treedata(roots):
                treelist = []

                for root in roots:
                    data = {'text': root.direction, 'selectable': False, 'id': root.id}
                    if root.id in alreadyjurisdiction:
                        data['state'] = {'checked': True}
                    children = root.children.all()
                    if len(children) > 0:
                        data['nodes'] = treedata(children)
                    treelist.append(data)

                return treelist

            tree = json.dumps(treedata(Resourcejurisdiction.objects.filter(parent=None).all()))
            mdata['jurisdictiondata'] = tree
        return render_to_response('jurisdiction_setup.html', mdata, context_instance=RequestContext(request))


def treedata(roots):
    treelist = []

    for root in roots:
        data = {'text': root.direction, 'selectable': False, 'id': root.id}
        # treelist.append(root.name)

        children = root.children.all()
        if len(children) > 0:
            data['nodes'] = treedata(children)
        treelist.append(data)

    return treelist
