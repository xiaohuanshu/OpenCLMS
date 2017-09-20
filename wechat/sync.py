from wechat.contact import contact_helper
from school.models import Class, Department
import logging

logger = logging.getLogger(__name__)
def department():
    departmentlist = contact_helper.department.get()
    for dep in departmentlist:
        if dep['parentid'] == 1:
            thisdepartmentid = dep['id']
            thisdepartment = Department.objects.get(name=dep['name'])
            cls = Class.objects.filter(department=thisdepartment).all()
            for c in cls:
                exist = False
                for d in departmentlist:
                    if c.name == d['name']:
                        exist = True
                        break
                if not exist:
                    logger.info("[updatedepartment] add department %s" % c.name)
                    contact_helper.department.create(c.name, thisdepartmentid)

    logger.info("[updatedepartment] Successful")