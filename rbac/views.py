from django.shortcuts import render_to_response, RequestContext

def jurisdiction_setup(request):
    return render_to_response('jurisdiction_setup.html', {}, context_instance=RequestContext(request))