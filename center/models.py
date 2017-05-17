from django.db import models
import os
from django.utils.http import urlquote
from django.conf import settings
from django.core.urlresolvers import reverse


# Create your models here.
class Filemodel(models.Model):
    file = models.FileField()

    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    def preview(self):
        extension = self.file_extension()
        office_extension = ['.docx', '.docm', '.dotm', '.dotx', '.xlsx', '.xlsb', '.xls', '.xlsm', '.pptx', '.ppsx',
                            '.ppt', '.pps', '.pptm', '.potm', '.ppam', '.potx', '.ppsm', 'doc']
        image_extension = ['.bmp', '.jpg', '.jpeg', '.png', '.gif']
        if extension in office_extension:
            url = "https://view.officeapps.live.com/op/embed.aspx?src=%s&wdStartOn=1&wdEmbedCode=0" % (
                urlquote("%s%s" % (settings.DOMAIN, self.file.url), safe=None))
            return url
        elif extension in image_extension:
            url = "%s?url=%s" % (reverse('course:imgview', args=[]), urlquote(self.file.url, safe=None))
            return url
        elif extension in [".bsh", ".c", ".cc", ".cpp", ".cs", ".csh", ".cyc", ".cv", ".htm", ".html", ".java", ".js",
                           ".m", ".mxml", ".perl", ".pl", ".pm", ".py", ".rb", ".sh", ".xhtml", ".xml", ".xsl"]:
            url = "%s?url=%s" % (reverse('course:codeview', args=[]), urlquote(self.file.url, safe=None))
            return url
        elif extension == '.pdf':
            return self.file.url
        elif extension == '.mp4':
            return self.file.url
        elif extension == '.txt':
            return self.file.url
        else:
            return None

    def isimage(self):
        image_extension = ['.bmp', '.jpg', '.jpeg', '.png', '.gif']
        if self.file_extension() in image_extension:
            return True
        else:
            return False

    def initialPreview(self):
        if self.isimage():
            return {'data': self.file.url, 'type': 'image'}
        elif self.file_extension() == '.pdf':
            return {'data': self.file.url, 'type': 'pdf'}
        elif self.file_extension() == '.mp4':
            return {'data': self.file.url, 'type': 'video', 'filetype': 'video/mp4'}
        else:
            return {'data': self.file.url, 'type': 'other'}

    def icon(self):
        extension = self.file_extension()
        icon = {
            'doc': '<i class="fa fa-file-word-o text-primary"></i>',
            'xls': '<i class="fa fa-file-excel-o text-success"></i>',
            'ppt': '<i class="fa fa-file-powerpoint-o text-danger"></i>',
            'pdf': '<i class="fa fa-file-pdf-o text-danger"></i>',
            'zip': '<i class="fa fa-file-archive-o text-muted"></i>',
            'htm': '<i class="fa fa-file-code-o text-info"></i>',
            'txt': '<i class="fa fa-file-text-o text-info"></i>',
            'mov': '<i class="fa fa-file-movie-o text-warning"></i>',
            'mp3': '<i class="fa fa-file-audio-o text-warning"></i>',
            'jpg': '<i class="fa fa-file-photo-o text-danger"></i>',
            'gif': '<i class="fa fa-file-photo-o text-muted"></i>',
            'png': '<i class="fa fa-file-photo-o text-primary"></i>'
        }
        if extension in ['.doc', '.docx']:
            return icon['doc']
        elif extension in ['.xls', '.xlsx']:
            return icon['xls']
        elif extension in ['.ppt', '.pptx']:
            return icon['ppt']
        elif extension in ['.zip', '.rar', '.tar', '.gzip', '.gz', '.7z']:
            return icon['zip']
        elif extension in ['.htm', '.html']:
            return icon['htm']
        elif extension in ['.txt', '.ini', '.csv', '.java', '.php', '.js', '.css', '.c', '.cpp', '.py']:
            return icon['txt']
        elif extension in ['.avi', '.mpg', '.mkv', '.mov', '.mp4', '.3gp', '.webm', '.wmv']:
            return icon['mov']
        elif extension in ['.mp3', '.wav']:
            return icon['mp3']
        elif extension == '.pdf':
            return icon['pdf']
        else:
            return '<i class="fa fa-file"></i>'

    class Meta:
        abstract = True
