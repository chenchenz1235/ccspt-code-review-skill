"""Behavior checks: independent expected values, safe evaluation, casts and unknown branches."""
import unittest
from unittest.mock import patch
from pathlib import Path
from calculate import evaluate,calculate,metadata_checks

class CalculatorTests(unittest.TestCase):
    def test_metadata_disabled_parameter_range(self):
        text='''void matlab_param_init(void)
{
/*{ ----------[控制(ctrl) 拖动(drag):1]---------- }*/
g_sys_ctrl_param.drag_speed_cmd_min = -1000; /*{ 单位:rpm; 最小值:0; 最大值:10000; 用户是否可见:1; 备注:拖动最低转速 }*/
/* 参数总个数和校验和 */
g_sys_ctrl_param.param_num = 0;
}
'''
        r=metadata_checks(text,{'drag_speed_cmd_min':-1000})
        self.assertEqual(r['groups'][0]['status'],'match')
        self.assertEqual(r['entries'][0]['range_status'],'outside_declared_range')
    def test_mapping_and_independent_baseline(self):
        refs=Path(__file__).resolve().parents[1]/'references'
        with patch("calculate.read_source") as reader, patch("pathlib.Path.read_bytes", return_value=b"fixture"):
            source=Path('fixture.c')
            reader.return_value='''void matlab_param_init(void)
{
g_sys_ctrl_param.pole_pairs = 5;
g_sys_ctrl_param.param6 = 275;
}
void matlab_calc_param_init(void)
{
g_sys_ctrl_param.rpm_to_radps_coef = 123;
g_sys_ctrl_param.test11 = (g_sys_ctrl_param.param6-245)*0.3;
if (g_sys_ctrl_param.pole_pairs > 0)
{
g_sys_ctrl_param.test7 = 2;
}
}
'''
            report=calculate(source,refs)
            c=next(x for x in report['baseline_checks'] if x['parameter']=='rpm_to_radps_coef')
            self.assertEqual(c['status'],'difference');self.assertAlmostEqual(c['expected'],5*6.28/60)
            m=next(x for x in report['indirect_decoding'] if x['parameter']=='test11')
            self.assertEqual(m['status'],'difference');self.assertEqual(m['expected'],6)
            self.assertEqual(report['conditional_assignments'][0]['name'],'test7')
    def test_safe_arithmetic(self):
        self.assertEqual(evaluate('(u32)(5.9)',{}),5)
        with self.assertRaises(ValueError):evaluate('(u32)(-1)',{})
        with self.assertRaises(ValueError):evaluate('__import__("os")',{})
        with self.assertRaises(ZeroDivisionError):evaluate('1/0',{})
        with self.assertRaises(ValueError):evaluate('(u32)(2.9) + 1',{})
        with self.assertRaises(KeyError):evaluate('missing+1',{})
if __name__=='__main__':unittest.main()

