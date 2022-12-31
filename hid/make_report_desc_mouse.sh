#!/bin/bash
echo -ne \\x05\\x01 > report_desc_mouse  # USAGE_PAGE (Generic Desktop)     0
echo -ne \\x09\\x02 >> report_desc_mouse # USAGE (Mouse)                    2
echo -ne \\xa1\\x01 >> report_desc_mouse # COLLECTION (Application)         4
echo -ne \\x09\\x01 >> report_desc_mouse #   USAGE (Pointer)                8
echo -ne \\xa1\\x00 >> report_desc_mouse #   COLLECTION (Physical)          10
echo -ne \\x05\\x09 >> report_desc_mouse #     USAGE_PAGE (Button)          12
echo -ne \\x19\\x01 >> report_desc_mouse #     USAGE_MINIMUM (Button 1)     14
echo -ne \\x29\\x02 >> report_desc_mouse #     USAGE_MAXIMUM (Button 2)     16
echo -ne \\x15\\x00 >> report_desc_mouse #     LOGICAL_MINIMUM (0)          18
echo -ne \\x25\\x01 >> report_desc_mouse #     LOGICAL_MAXIMUM (1)          20
echo -ne \\x75\\x01 >> report_desc_mouse #     REPORT_SIZE (1)              22
echo -ne \\x95\\x02 >> report_desc_mouse #     REPORT_COUNT (2)             24
echo -ne \\x81\\x02 >> report_desc_mouse #     INPUT (Data,Var,Abs)         26
echo -ne \\x95\\x06 >> report_desc_mouse #     REPORT_COUNT (6)             28
echo -ne \\x81\\x03 >> report_desc_mouse #     INPUT (Cnst,Var,Abs)         30
echo -ne \\x05\\x01 >> report_desc_mouse #     USAGE_PAGE (Generic Desktop) 32
echo -ne \\x09\\x30 >> report_desc_mouse #     USAGE (X)                    34
echo -ne \\x09\\x31 >> report_desc_mouse #     USAGE (Y)                    36
echo -ne \\x15\\x81 >> report_desc_mouse #     LOGICAL_MINIMUM (-127)       38
echo -ne \\x25\\x7f >> report_desc_mouse #     LOGICAL_MAXIMUM (127)        40
echo -ne \\x75\\x08 >> report_desc_mouse #     REPORT_SIZE (8)              42
echo -ne \\x95\\x02 >> report_desc_mouse #     REPORT_COUNT (2)             44
echo -ne \\x81\\x06 >> report_desc_mouse #     INPUT (Data,Var,Rel)         46
echo -ne \\xc0  >> report_desc_mouse #   END_COLLECTION                 48
echo -ne \\xc0  >> report_desc_mouse # END_COLLECTION
