from sys import stdout

from django.core.management.base import BaseCommand

from django.conf import settings

from ...dbdoc import ModelWriter


class Command(BaseCommand):
    def parse_model(self, module):
        from importlib import import_module
        if type(module) == str:
            module = import_module(module)
        return [m for m in module.__dict__.values() if hasattr(m, '_meta') and m._meta.model]

    def handle(self, *args, **options):
        # 创建文件
        sbuf = stdout
        sbuf.write('.. _table:\n\n******\n表结构\n******\n')
        # models = [m for m in settings.DBDOC_MODELS if hasattr(m, '_meta') and m._meta.model]

        models = []
        for module in settings.DBDOC_MODELS:
            models += self.parse_model(module)

        model_results = dict()
        m2m_results = dict()

        for model in models:

            model_writer = ModelWriter(model)
            model_results[model_writer.get_table_name()] = model_writer.render()

            for table_name, content in model_writer.render_m2m_tables().items():
                m2m_results[table_name] = content

        result = dict(**model_results)
        for table_name, content in m2m_results.items():
            if table_name not in result:
                result[table_name] = content

        for table_name, content in sorted(result.items()):
            sbuf.write(content)

        sbuf.close()
