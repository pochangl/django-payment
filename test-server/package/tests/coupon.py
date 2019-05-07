import datetime
from django.test import TestCase
from django.utils.timezone import now
from payment.models import Code
from payment.serializers import CodeField
from rest_framework  import serializers
from rest_framework.exceptions import ValidationError


class CodeMixin:
    def get_pre_save_code(self, **kwargs):
        delta = datetime.timedelta(days=1)
        data = {
            'time_start': now() - delta,
            'time_end': now() + delta
        }

        data.update(kwargs)
        return Code(**data)

    def create_code(self, **kwargs):
        code = self.get_pre_save_code(**kwargs)
        code.save()
        return code


class TestCodeGeneration(CodeMixin, TestCase):
    def test_code_generation(self):
        code = self.get_pre_save_code()
        self.assertIsNone(code.code)
        code.save()
        self.assertTrue(code.code)

    def test_post_save_before_save(self):
        code = self.get_pre_save_code()
        with self.assertRaises(Exception):
            code.post_save()

        self.assertIsNone(code.code)

    def test_ignore_second_save(self):
        code = self.get_pre_save_code()
        self.assertIsNone(code.code)
        code.save()
        code_code = code.code
        code.save()
        self.assertEqual(code.code, code_code)

    def test_pre_set_code(self):
        code = self.get_pre_save_code()
        code.code = 'tom'
        code.save()
        self.assertEqual(code.code, 'tom')

    def test_str(self):
        code = self.get_pre_save_code()
        code.save()
        self.assertTrue(str(code), code.code)

    def test_is_active(self):
        code = self.create_code()
        self.assertTrue(code.is_valid())

    def test_inactive(self):
        code = self.create_code()
        self.assertTrue(code.is_valid())
        code.is_active = False
        self.assertFalse(code.is_valid())

    def test_outdated(self):
        code = self.create_code()
        self.assertTrue(code.is_valid())
        code.time_end = code.time_start
        self.assertFalse(code.is_valid())

    def test_not_yet(self):
        code = self.create_code()
        self.assertTrue(code.is_valid())
        code.time_start = code.time_end
        self.assertFalse(code.is_valid())

    def test_actives(self):
        code = self.create_code()
        code1 = self.create_code(time_start=code.time_end)
        code2 = self.create_code(time_end=code.time_start)
        code3 = self.create_code(is_active=False)

        self.assertEqual(Code.objects.count(), 4)
        self.assertEqual(Code.objects.actives().get(), code)

    def test_deactivate(self):
        code = self.create_code()
        self.assertTrue(code.is_valid())
        code.deactivate()
        self.assertFalse(code.is_valid())

class TestCodeField(CodeMixin, TestCase):
    class Serializer(serializers.Serializer):
        code = CodeField()

        class Meta:
            fields = ('code',)

    def test_to_internal(self):
        code = self.create_code()
        serializer = self.Serializer(data={
            'code': code.code
        })

        self.assertTrue(serializer.is_valid())
        internal = serializer.validated_data['code']
        self.assertEqual(code, internal)

    def test_no_code(self):
        code = self.create_code()

        serializer = self.Serializer(data={
            'code': code.code[:-1]
        })

        with self.assertRaises(ValidationError):
            self.assertFalse(serializer.is_valid(raise_exception=True))

    def test_to_representation(self):
        code = self.create_code()
        serializer = self.Serializer(instance=code)
        self.assertEqual(serializer.data['code'], code.code)
