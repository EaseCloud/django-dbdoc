class ModelWriterColumn:
    width = 12
    label = '<unnamed col>'

    @classmethod
    def str_width(cls, s):
        return sum([min(len(c.encode()), 2) for c in s])

    @classmethod
    def justify(cls, s):
        """ 对齐字符串宽度，右侧补空格
        计算字符串的宽度，中文字符宽度为 2
        :return:
        """
        width = cls.str_width(s)
        return s + ' ' * (cls.width - width)

    @classmethod
    def render(cls, field):
        raise NotImplementedError('Must override')

    @classmethod
    def render_header(cls):
        return cls.justify(cls.label) + '|'


class NameColumn(ModelWriterColumn):
    width = 26
    label = '字段'

    @classmethod
    def render(cls, field):
        return cls.justify(field.name) + '|'


class AiColumn(ModelWriterColumn):
    width = 4
    label = '自增'

    @classmethod
    def render(cls, field):
        from django.db import connection
        return cls.justify(
            'Y' if 'AUTO_INCREMENT' in str(field.db_type(connection)) else '') + '|'


class NullColumn(ModelWriterColumn):
    width = 4
    label = '空'

    @classmethod
    def render(cls, field):
        return cls.justify('Y' if field.null else '') + '|'


class TypeColumn(ModelWriterColumn):
    width = 23
    label = '类型'

    @classmethod
    def render(cls, field):
        from django.db import connection
        return cls.justify(
            str(field.db_type(connection)).replace('AUTO_INCREMENT', '').strip()
        ) + '|'


class PKColumn(ModelWriterColumn):
    width = 4
    label = '主键'

    @classmethod
    def render(cls, field):
        return cls.justify('Y' if field.primary_key else '') + '|'


class FKColumn(ModelWriterColumn):
    width = 4
    label = '外键'

    @classmethod
    def render(cls, field):
        return cls.justify('Y' if field.many_to_one or field.one_to_one else '') + '|'


class VerboseNameColumn(ModelWriterColumn):
    width = 25
    label = '名称'

    @classmethod
    def render(cls, field):
        return cls.justify(str(field.verbose_name)) + '|'


class ModelWriter:
    # 输出md中表格各列长度
    field_name_length = 26
    field_null_length = 5
    field_type_length = 23
    field_pk_length = 3
    field_fk_length = 3
    field_verbose_name_length = 25

    columns = [
        NameColumn,
        VerboseNameColumn,
        TypeColumn,
        PKColumn,
        AiColumn,
        NullColumn,
        FKColumn,
    ]

    def __init__(self, model_class):
        self.model = model_class

    def get_separator(self):

        return '\n+' + \
               '+'.join(column.width * '-' for column in self.columns) + \
               '+\n'

    def get_table_name(self):
        return self.model._meta.db_table

    def get_table_verbose_name(self):
        return str(self.model._meta.verbose_name)

    def is_model(self):
        from django.db.models.base import ModelBase
        return type(self.model) == ModelBase

    def is_m2m(self):
        from django.db.models.fields.related import ManyToManyField
        return type(self.model) == ManyToManyField

    # def get_title(self):
    #     from django.db.models.base import ModelBase
    #     from django.db.models.fields.related import ManyToManyField
    #     if type(self.model) == ManyToManyField:
    #         return self.get_table_name()
    #     elif type(self.model) == ModelBase:
    #         return '{} ({})'.format(self.get_table_name(), self.get_table_verbose_name())
    #     else:
    #         return '**未定义数据表**'

    def get_fields(self):
        return self.model._meta.get_fields()

    def render_title(self, sbuf):
        sbuf.write('\n')
        sbuf.write(self.get_table_name())
        sbuf.write('\n')
        sbuf.write(''.ljust(ModelWriterColumn.str_width(self.get_table_name()), '^'))
        sbuf.write('\n')
        if self.is_model():
            sbuf.write(str(self.get_table_verbose_name()))
            sbuf.write('\n')

    def render_header(self, sbuf):
        sbuf.write('|' + ''.join(col.render_header() for col in self.columns))

    def render_field(self, field, sbuf):
        from django.db.models import OneToOneRel, ManyToOneRel
        if field.one_to_many \
                or field.many_to_many \
                or type(field) in [OneToOneRel, ManyToOneRel]:
            return

        field_row = '|'
        for column in self.columns:
            field_row += column.render(field)
        sbuf.write(field_row)
        sbuf.write(self.get_separator())

    def render_m2m_tables(self):
        """ 渲染所有的 M2M 字段
        :return: 返回一个字典，key 为数据库表名，value 为渲染获得的结果字符串
        """
        result = dict()

        for field in self.get_fields():
            from django.db.models import ManyToManyField
            if type(field) == ManyToManyField and hasattr(field, 'm2m_field_name'):
                m2m_writer = M2MModelWriter(field)
                result[field.m2m_db_table()] = m2m_writer.render()
        return result

    def render(self):

        model = self.model

        # 抽象类 如：EntityModel没有表
        if hasattr(model, '_meta') and model._meta.abstract:
            return ''

        from io import StringIO

        sbuf = StringIO()

        self.render_title(sbuf)

        # 线rn
        sbuf.write(self.get_separator())
        self.render_header(sbuf)

        # print(self.model._meta.db_table)

        # 线 rn
        sbuf.write(self.get_separator())
        for field in self.get_fields():
            self.render_field(field, sbuf)
            # print(field)
            # print(field.name)                 # 字段名
            # print(field.null)                 # 是否为空
            # print(field.max_length)           # 长度
            # print(field.db_type(connection))  # 类型
            # print(field.get_internal_type())  # django类型
            # print(field.many_to_many)         # 是否多对多 返回true
            # print(field.primary_key)          # 是否为主键
            # print(field.one_to_many)          # fields 的model 对本model的外键
            # print(field.many_to_one)          # 外键   数据库字段名 field+'_id'

        sbuf.seek(0)
        return sbuf.read()


class M2MModelWriter(ModelWriter):
    class VirtualField:
        def __init__(self, **kwargs):
            self.one_to_many = False
            self.many_to_many = False
            self.many_to_one = False
            self.one_to_one = False
            for k, v in kwargs.items():
                setattr(self, k, v)

    def get_table_name(self):
        return self.model.m2m_db_table()

    def get_fields(self):
        model_a = self.model.remote_field.model
        model_b = self.model.remote_field.field.model
        return [
            # Primary ID Column
            self.model.target_field,
            # Side-A model
            self.VirtualField(
                name=model_a._meta.model_name + '_id',
                null=False,
                verbose_name=model_a._meta.verbose_name,
                db_type=model_a._meta.pk.db_type,
                primary_key=False,
                many_to_one=True,
            ),
            # Side-B model
            self.VirtualField(
                name=model_b._meta.model_name + '_id',
                null=False,
                verbose_name=model_b._meta.verbose_name,
                db_type=model_b._meta.pk.db_type,
                primary_key=False,
                many_to_one=True,
            ),
        ]
