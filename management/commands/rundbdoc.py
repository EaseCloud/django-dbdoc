import traceback
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_arguments('models_child',child)

    def handle(self, *args, **options):
        import core.models
        # 输出md中表格各列长度
        field_name_length = 26
        field_null_length = 5
        field_type_length = 23
        field_pk_length = 3
        field_fk_length = 3
        # 创建文件
        output_plan = 'index.rst'
        output_obj = open(output_plan, 'w')
        output_obj.write('.. _table:\n\n******\n表结构\n******\n')
        models = [m for m in core.models.__dict__.values() if hasattr(m, '_meta') and m._meta.model]
        # +-----------+--------------------—+ 线 line_top
        # +-----------+------+-----+--------+ 线 line_normal
        # +-----------+------+-----+--------+ 线 line_normal
        line_top = '\n{}{}{}\n'.format('+'.ljust(field_name_length + 1, '-'), '+'.ljust(
            field_null_length + field_type_length + field_pk_length + field_fk_length + 4, '-'), '+')
        line_normal = '\n{}{}{}{}{}{}\n'.format('+'.ljust(field_name_length + 1, '-'),
                                                '+'.ljust(field_null_length + 1, '-'),
                                                '+'.ljust(field_type_length + 1, '-'),
                                                '+'.ljust(field_pk_length + 1, '-'),
                                                '+'.ljust(field_fk_length + 1, '-'), '+')
        manytomany_fields = []
        for model in models:
            # print(model._meta.verbose_name)
            if not model._meta.abstract:  # 抽象类 如：EntityModel没有表
                output_obj.write('\n')
                # 线r1
                # output_obj.write(line_top)
                # output_obj.write('|')
                # output_obj.write('table'.ljust(field_name_length))
                # output_obj.write('|')
                output_obj.write(str(model._meta.db_table))
                output_obj.write('\n')
                output_obj.write('^'.ljust(len(str(model._meta.db_table)), '^'))
                output_obj.write('\n')
                # output_obj.write('|')
                # 线rn
                output_obj.write(line_normal)
                output_obj.write('|')
                output_obj.write('field'.ljust(field_name_length))
                output_obj.write('|')
                output_obj.write('null'.ljust(field_null_length))
                output_obj.write('|')
                output_obj.write('type'.ljust(field_type_length))
                output_obj.write('|')
                output_obj.write('pk'.ljust(field_pk_length))
                output_obj.write('|')
                output_obj.write('fk'.ljust(field_fk_length))
                output_obj.write('|')
                # 线 rn
                output_obj.write(line_normal)
                for field in model._meta.get_fields():
                    try:
                        if field.one_to_many:
                            continue
                        elif field.many_to_many:
                            # ManytoMany
                            # print(field.name)
                            # print(field.model._meta.db_table)
                            # print(field.related_model)
                            manytomany_fields.append(field)
                        elif field.many_to_one or field.one_to_one:
                            # foreign_key or OneToOne
                            field_name_col = '{}_id'.format(field.name).ljust(field_name_length)
                            field_null_col = ('Y' if field.null else 'N').ljust(field_null_length)
                            field_type_col = str(field.db_type(connection)).ljust(field_type_length)
                            field_pk_col = ('Y' if field.primary_key else 'N').ljust(field_pk_length)
                            field_fk_col = ('Y' if field.many_to_one or field.one_to_one else 'N').ljust(
                                field_fk_length)
                            field_row = '|{}|{}|{}|{}|{}|'.format(
                                field_name_col, field_null_col, field_type_col, field_pk_col, field_fk_col)
                            output_obj.write(field_row)
                            output_obj.write(line_normal)
                        else:
                            field_name_col = field.name.ljust(field_name_length)
                            field_null_col = ('Y' if field.null else 'N').ljust(field_null_length)
                            field_type_col = str(field.db_type(connection)).ljust(field_type_length)
                            field_pk_col = ('Y' if field.primary_key else 'N').ljust(field_pk_length)
                            field_fk_col = 'N'.ljust(field_fk_length)
                            field_row = '|{}|{}|{}|{}|{}|'.format(
                                field_name_col, field_null_col, field_type_col, field_pk_col, field_fk_col)
                            output_obj.write(field_row)
                            output_obj.write(line_normal)
                    except Exception as e:
                        # print(field.many_to_many)
                        # print(field.one_to_many)
                        # print(field.many_to_one)
                        # print(field.name)
                        continue
        for manytomany_field in manytomany_fields:
            # print(manytomany_field.m2m_db_table())
            try:
                # print(manytomany_field.m2m_db_table())    # ManyToMany 中间表表名
                # print(manytomany_field.m2m_field_name())  # ManyToMany 中间表第一个字段
                # print(manytomany_field.m2m_reverse_field_name())  # ManyToMany 中间表另一个字段
                manytomany_db_name = manytomany_field.m2m_db_table()
                output_obj.write('\n')
                # output_obj.write(line_top)
                # output_obj.write(
                #     '|{}|{}'.format('table'.ljust(field_name_length), str(manytomany_db_name).ljust(
                #         field_null_length + field_type_length + field_pk_length + field_fk_length + 3)))
                output_obj.write(str(manytomany_db_name))
                output_obj.write('\n')
                output_obj.write('^'.ljust(len(str(manytomany_db_name)), '^'))
                # output_obj.write('|')
                output_obj.write(line_normal)
                output_obj.write('|')
                output_obj.write('field'.ljust(field_name_length))
                output_obj.write('|')
                output_obj.write('null'.ljust(field_null_length))
                output_obj.write('|')
                output_obj.write('type'.ljust(field_type_length))
                output_obj.write('|')
                output_obj.write('pk'.ljust(field_pk_length))
                output_obj.write('|')
                output_obj.write('fk'.ljust(field_fk_length))
                output_obj.write('|')
                output_obj.write(line_normal)

                output_obj.write('|')
                output_obj.write('id'.ljust(field_name_length))
                output_obj.write('|')
                output_obj.write('N'.ljust(field_null_length))
                output_obj.write('|')
                output_obj.write('integer AUTO_INCREMENT'.ljust(field_type_length))
                output_obj.write('|')
                output_obj.write('Y'.ljust(field_pk_length))
                output_obj.write('|')
                output_obj.write('N'.ljust(field_fk_length))
                output_obj.write('|')
                output_obj.write(line_normal)

                output_obj.write('|')
                field_name_col = '{}_id'.format(manytomany_field.m2m_field_name()).ljust(field_name_length)
                output_obj.write(field_name_col)
                output_obj.write('|')
                output_obj.write('N'.ljust(field_null_length))
                output_obj.write('|')
                output_obj.write('integer'.ljust(field_type_length))
                output_obj.write('|')
                output_obj.write('N'.ljust(field_pk_length))
                output_obj.write('|')
                output_obj.write('Y'.ljust(field_fk_length))
                output_obj.write('|')
                output_obj.write(line_normal)

                field_reverse_name_col = '{}_id'.format(manytomany_field.m2m_reverse_field_name()).ljust(
                    field_name_length)
                output_obj.write('|')
                output_obj.write(field_reverse_name_col)
                output_obj.write('|')
                output_obj.write('N'.ljust(field_null_length))
                output_obj.write('|')
                output_obj.write('integer'.ljust(field_type_length))
                output_obj.write('|')
                output_obj.write('N'.ljust(field_pk_length))
                output_obj.write('|')
                output_obj.write('Y'.ljust(field_fk_length))
                output_obj.write('|')
                output_obj.write(line_normal)
            except Exception as e:
                continue
                # print(manytomany_field.name)
                # print(manytomany_field.model._meta.db_table)
                # print(manytomany_field.related_model._meta.db_table)
                # print(manytomany_field.is_relation)
                # if model._meta.db_table == 'core_insurance_order':
                #     for field in model._meta.get_fields():
                #         print(field.name)
                #         print(field.many_to_many)
                #         print(field.one_to_many)
                #         print(field.many_to_one)
                #         print(field.get_internal_type)
                #         print(field.name)
                #         try:
                #             print(field.db_type(connection))
                #             print(field.many_to_one)
                #             print(field.one_to_many)
                #         except Exception as e:
                #             print('this is GenericForeignKey')


                # for field in model._meta.get_fields():
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

        # 新建md文件
        # output_plan = 'dbdoc.md'
        # output_obj = open(output_plan, 'w')
        # output_obj.write("22222")
        output_obj.close()
        self.stdout.write(self.style.SUCCESS('SUCCESS Command'))
