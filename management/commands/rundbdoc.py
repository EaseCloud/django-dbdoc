from sys import stdout

from django.core.management.base import BaseCommand

from ...dbdoc import ModelWriter


class Command(BaseCommand):
    def handle(self, *args, **options):
        import core.models
        # 创建文件
        sbuf = stdout
        sbuf.write('.. _table:\n\n******\n表结构\n******\n')
        models = [m for m in core.models.__dict__.values() if hasattr(m, '_meta') and m._meta.model]

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
