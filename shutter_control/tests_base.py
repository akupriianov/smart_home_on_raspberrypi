import re
from django.test import TestCase

class VerboseTestCase(TestCase):
    """
    Klasa bazowa zapewniająca dodatkowe logowanie PASS/FAIL/ERROR dla każdego testu.
    """

    def run(self, result=None):
        """
        Nadpisujemy domyślną metodę run() z unittest.TestCase,
        aby po wykonaniu testu sprawdzić w obiekcie result, czy test się udał.
        """
        super_result = super().run(result)
        
        # Jeżeli result istnieje (czyli jest to standardowy test runner)
        if result:
            test_id = self.id()  # np. "app.tests.MyTestCase.test_something"
            # Możemy wyłuskać samą nazwę metody testowej:
            test_method_name = test_id.split('.')[-1]

            # Sprawdzamy czy test jest na liście błędów, porażek lub pominiętych
            is_failed = any(test_id in str(fail[0]) for fail in result.failures)
            is_errored = any(test_id in str(err[0]) for err in result.errors)
            is_skipped = any(test_id in str(skp[0]) for skp in result.skipped)

            if is_failed:
                print(f"[FAILED]  {test_method_name}")
            elif is_errored:
                print(f"[ERROR]   {test_method_name}")
            elif is_skipped:
                print(f"[SKIPPED] {test_method_name}")
            else:
                print(f"[PASSED]  {test_method_name}")

        return super_result