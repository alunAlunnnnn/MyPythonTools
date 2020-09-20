# -------------------------------------------------------------------------------
# Name:        CommonLib
# Purpose:     Contains common functions
#
# Author:      Gert van Maren
#
# Created:     14/12/2016
# Copyright:   (c) Esri 2016
# updated:
# updated:
# updated:

# -------------------------------------------------------------------------------

import arcpy
import os
import time
import traceback
import datetime
import logging
import sys
import math
from math import *

# Constants
NON_GP = "non-gp"
ERROR = "error"
WARNING = "warning"

# ----------------------------Template Functions----------------------------#

in_memory_switch = True

def template_function(debug):

    if debug == 1:
        msg("--------------------------")
        msg("Executing template_function...")

    start_time = time.clock()

    try:

        pass

        msg_prefix = "Function template_function completed successfully."
        failed = False

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "template_function",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


class FunctionError(Exception):

    """
    Raised when a function fails to run.
    """

    pass


def trace(*arg):

    """
    Trace finds the line, the filename
    and error message and returns it
    to the user
    """

    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # script name + line number
    line = tbinfo.split(", ")[1]

    # Get Python syntax error
    synerror = traceback.format_exc().splitlines()[-1]

    if len(arg) == 0:
        return line, __file__, synerror
    else:
        return line, arg[1], synerror


def set_up_logging(output_folder, file):

    arcpy.AddMessage("Executing set_up_logging...")
    start_time = time.clock()

    try:
        # Make the 'logs' folder if it doesn't exist
        log_location = output_folder
        if not os.path.exists(log_location):
            os.makedirs(log_location)

        # Set up logging
        logging.getLogger('').handlers = []  # clears handlers
        date_prefix = datetime.datetime.now().strftime('%Y%m%d_%H%M')

        log_file_date = os.path.join(log_location, file + "_" + date_prefix + ".log")
        log_file = os.path.join(log_location, file + ".log")
        log_file_name = log_file
        date_prefix = date_prefix + "\t"  # Inside messages, an extra tab to separate date and any following text is desirable

        if os.path.exists(log_file):
            try:
                os.access(log_file, os.R_OK)
                log_file_name = log_file
            except FunctionError:
                log_file_name = log_file_date

        logging.basicConfig(level=logging.INFO,
                            filename=log_file_name,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        msg("Logging set up.  Log location: " + log_location)

        failed = False

    except:
        failed = True
        raise

    finally:
        if failed:
            msg_prefix = "An exception was raised in set_up_logging."
            end_time = time.clock()
            msg_body = create_msg_body(msg_prefix, start_time, end_time)
            msg(msg_body, ERROR)


def msg(*arg):

    # Utility method that writes a logging info statement, a print statement and an
    # arcpy.AddMessage() statement all at once.
    if len(arg) == 1:
        logging.info(str(arg[0]) + "\n")
        arcpy.AddMessage(str(arg[0]))
    elif arg[1] == ERROR:
        logging.error(str(arg[0]) + "\n")
        arcpy.AddError(str(arg[0]))
    elif arg[1] == WARNING:
        logging.warning(str(arg[0]) + "\n")
        arcpy.AddWarning(str(arg[0]))
    elif arg[1] == NON_GP:
        logging.info(str(arg[0]) + "\n")
        arcpy.AddMessage(str(arg[0]))
#    print(str(arg[0]))

    return


def create_msg_body(msg_prefix, start_time, end_time):

    # Creates the message returned after each run of a function (successful or unsuccessful)
    diff = end_time - start_time

    if diff > 0:
        if msg_prefix == "":
            msg_prefix = "Elapsed time: "
        else:
            msg_prefix = msg_prefix + "  Elapsed time: "

        elapsed_time_mins = int(math.floor(diff/60))
        minutes_txt = " minutes "
        if elapsed_time_mins == 1:
            minutes_txt = " minute "
        if elapsed_time_mins > 0:
            elapsed_time_secs = int(round(diff - (60 * elapsed_time_mins)))
            seconds_txt = " seconds."
            if elapsed_time_secs == 1:
                seconds_txt = " second."
            elapsed_time_formatted = str(elapsed_time_mins) + minutes_txt + str(elapsed_time_secs) + seconds_txt
        else:
            elapsed_time_secs = round(diff - (60 * elapsed_time_mins), 2)
            seconds_txt = " seconds."
            if elapsed_time_secs == 1:
                seconds_txt = " second."
            elapsed_time_formatted = str(elapsed_time_secs) + seconds_txt

        msg_body = msg_prefix + elapsed_time_formatted

    else:
        msg_body = msg_prefix

    return msg_body


def log_message(inFile, message):
    directory = os.path.dirname(inFile)
    if not os.path.exists(directory):
        os.makedirs(directory)

    text_file = open(inFile, "a")
    text_file.write(message + "\n")
    text_file.close()


def create_gdb(path, name):
    try:
        int_gdb = os.path.join(path, name)

        if not arcpy.Exists(int_gdb):
            arcpy.CreateFileGDB_management(path, name, "CURRENT")
            return int_gdb
        else:
            return int_gdb

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])


def get_name_from_feature_class(feature_class):
    desc_fc = arcpy.Describe(feature_class)
    return desc_fc.name


def is_layer(layer):
    desc_fc = arcpy.Describe(layer)
    if hasattr(desc_fc, "nameString"):
        return 1
    else:
        return 0


def get_full_path_from_layer(in_layer):
    dir_name = os.path.dirname(arcpy.Describe(in_layer).catalogPath)
    layer_name = arcpy.Describe(in_layer).name

    return os.path.join(dir_name, layer_name)


# Get Workspace from Building feature class location
def get_work_space_from_feature_class(feature_class, get_gdb):
    dir_name = os.path.dirname(arcpy.Describe(feature_class).catalogPath)
    desc = arcpy.Describe(dir_name)

    if hasattr(desc, "datasetType") and desc.datasetType == 'FeatureDataset':
        dirname = os.path.dirname(dir_name)

    if get_gdb == "yes":
        return dir_name
    else:  # directory where gdb lives
        return os.path.dirname(dir_name)


# Field Exists
def field_exist(feature_class, field_name):
    field_list = arcpy.ListFields(feature_class, field_name)
    field_count = len(field_list)
    if field_count == 1:
        return True
    else:
        return False


# Define DeleteAdd Fields
def delete_add_field(feature_class, field, field_type):
    try:
        if field_exist(feature_class, field):
            arcpy.DeleteField_management(feature_class, field)

        arcpy.AddField_management(feature_class, field, field_type, None, None, None,
                                      None, "true", "false", None)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])


def get_feature_count(feature_class, query):
    fields = arcpy.ListFields(feature_class)
    count = 0

    with arcpy.da.SearchCursor(feature_class, str(fields[0].name), query) as cursor:
        for row in cursor:
            count += 1

    return count


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def get_fids_for_selection(lyr):
    try:
        desc = arcpy.Describe(lyr)
        fid_list = desc.FIDSet.split(";")

        return fid_list, len(fid_list)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])


def check_null_in_fields(cn_table, cn_field_list, error, debug):
    try:
        if debug == 1:
            msg("--------------------------")
            msg("Executing check_null_in_fields...")

        start_time = time.clock()
        failed = True
        null_value = False
        field_name = ""

        if arcpy.Exists(cn_table):
            with arcpy.da.SearchCursor(cn_table, cn_field_list) as cursor:
                for row in cursor:
                    i = 0
                    for field in cn_field_list:
                        if row[i] is None:
                            null_value = True
                            field_name = field
                            break

                        i += 1

                    if null_value is True:
                        if error:
                            msg_prefix = "Found at least 1 NULL value in attribute " + field_name + " in " + get_name_from_feature_class(cn_table)
                            msg_body = create_msg_body(msg_prefix, 0, 0)
                            msg(msg_body, "warning")

                        break

        msg_prefix = "Function check_null_in_fields completed successfully."
        failed = False
        return null_value

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "check_null_in_fields",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)
            else:
                pass


def check_fields(cf_table, cf_field_list, error, debug):
    try:
        if debug == 1:
            msg("--------------------------")
            msg("Executing check_fields...")

        start_time = time.clock()

        real_fields_list = []
        real_fields = arcpy.ListFields(cf_table)
        i = 0

        for f in real_fields:
            real_fields_list.append(f.name)

        for s in cf_field_list:
            if s not in real_fields_list:
                i = 1
                if error:
                    msg_prefix = "Can't find " + s + " in " + cf_table
                    msg_body = create_msg_body(msg_prefix, 0, 0)
                    msg(msg_body, "error")

        msg_prefix = "Function check_fields completed successfully."
        failed = False

        return i

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "check_fields",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)
            else:
                pass


def add_field(feature_class, field, field_type, length):
    try:
        if not field_exist(feature_class, field):
            arcpy.AddField_management(feature_class, field, field_type, field_length=length)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])

# Define DeleteAdd Fields
def delete_fields(feature_class, field_list):
    try:
        for f in field_list:
            if field_exist(feature_class, f):
                arcpy.DeleteField_management(feature_class, f)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])


def find_field_by_wildcard(feature_class, wild_card):
    try:
        real_fields = arcpy.ListFields(feature_class)

        for f in real_fields:
            field_name = f.name
            if wild_card in field_name:
                return field_name
                break

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])

def delete_fields_by_wildcard(feature_class, wild_card, fields_to_keep):
    try:
        real_fields = arcpy.ListFields(feature_class)

        for f in real_fields:
            field_name = f.name
            if wild_card in field_name:
                if f.name not in fields_to_keep:
                    arcpy.DeleteField_management(feature_class, f.name)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])

def get_fields_by_wildcard(feature_class, wild_card, fields_to_skip):
    try:
        real_fields = arcpy.ListFields(feature_class)
        field_list = []

        for f in real_fields:
            field_name = f.name
            if wild_card in field_name:
                if f.name not in fields_to_skip:
                    field_list.append(field_name)

        return(field_list)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])



def copy_features_with_selected_attributes(ws, input_obj, output_obj, keep_fields_list, where_clause, debug):
    # Make an ArcGIS Feature class, containing only the fields
    # specified in keep_fields_list, using an optional SQL query. Default
    # will create a layer/view with NO fields. '
    try:
        if debug == 1:
            msg("--------------------------")
            msg("Executing check_fields...")

        start_time = time.clock()

        field_info_str = ''

        input_fields = arcpy.ListFields(input_obj)

        if not keep_fields_list:
            keep_fields_list = []
        for field in input_fields:
            if field.name in keep_fields_list:
                field_info_str += field.name + ' ' + field.name + ' VISIBLE;'
            else:
                field_info_str += field.name + ' ' + field.name + ' HIDDEN;'

        field_info_str.rstrip(';')  # Remove trailing semicolon

        featureLayer = "feature_lyr"
        arcpy.MakeFeatureLayer_management(input_obj, featureLayer, where_clause, field_info=field_info_str)

        if arcpy.Exists(output_obj):
            arcpy.Delete_management(output_obj)

        arcpy.CopyFeatures_management(featureLayer, output_obj)

        msg_prefix = "Function copy_features_with_selected_attributes completed successfully."
        failed = False

        return output_obj

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "copy_features_with_selected_attributes",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)
            else:
                pass


def remove_layers_from_scene(project, layer_list):
    start_time = time.clock()
    try:
        msg_prefix = ""

        for m in project.listMaps():  # cycle through the available SCENEs
            if m.mapType == "SCENE":
                for lyr in m.listLayers():
                    if lyr.name in layer_list:
                        layer_name = lyr.name
                        m.removeLayer (lyr)
                        msg_prefix = "Removed " + layer_name + " from project pane."
        failed = False

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "remove_layers_from_scene",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            msg(msg_body)


def import_table_with_required_fields(in_table, ws, out_table_name, local_list, debug):

    if debug == 1:
        msg("--------------------------")
        msg("Executing import_table_with_required_fields...")

    start_time = time.clock()

    try:
        i = 0
        msg_prefix = ""

        result = arcpy.TableToTable_conversion(in_table, ws, out_table_name)

        if result.status == 4:
            # check necessary fields
            if check_fields(ws + "\\" + out_table_name, local_list, True, debug) == 0:
                msg_prefix = "Function import_table_with_required_fields completed successfully."
            else:
                i = 1
        else:
            i = 1

        failed = False
        return i, ws + "\\" + out_table_name

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "import_table_with_required_fields",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)
            pass


def get_z_unit(local_lyr, debug):

    if debug == 1:
        msg("--------------------------")
        msg("Executing get_z_unit...")

    start_time = time.clock()

    try:

        sr = arcpy.Describe(local_lyr).spatialReference
        local_unit = 'Meters'

        if sr.VCS:
            unit_z = sr.VCS.linearUnitName
        else:
            unit_z = sr.linearUnitName
            msg_body = ("Could not detect a vertical coordinate system for " + get_name_from_feature_class(local_lyr))
            msg(msg_body, WARNING)
            msg_body = ("Using linear units instead.")
            msg(msg_body)

        if unit_z in ('Foot', 'Foot_US', 'Foot_Int'):
            local_unit = 'Feet'
        else:
            local_unit = 'Meters'

        msg_prefix = "Function get_z_unit completed successfully."
        failed = False

        return local_unit

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "get_z_unit",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


def get_row_values_for_fields_with_floatvalue(lyr, table, fields, select_field, value):
#    msg("--------------------------")
#    msg("Executing get_row_values_for_selected_fields...")
    start_time = time.clock()

    try:
        debug = 0
        value_list = []
        type_list = []
        length_list = []
        check_list = list(fields)
        if select_field is not None:
            check_list.append(select_field)
        return_error = True

        if lyr:
            searchInput = lyr
        else:
            searchInput = get_full_path_from_layer(table)

        if arcpy.Exists(searchInput):
            real_fields = arcpy.ListFields(searchInput)
            if value == "no_expression":
                expression = None
            else:
                expression = arcpy.AddFieldDelimiters(table, select_field) + " = " + str(value)

            if check_fields(searchInput, check_list, return_error, 0) == 0:
                with arcpy.da.SearchCursor(searchInput, fields, expression) as cursor:
                    for row in cursor:
                        i = 0
                        for field in fields:
                            value_list.append(row[i])

                            # for real_field in real_fields:
                            #     if real_field.name == field:
                            #         type_list.append(real_field.type)
                            #         length_list.append(real_field.length)
                            #         break
                            i += 1

        msg_prefix = "Function get_row_values_for_selected_fields completed successfully."
        failed = False

        return value_list

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "get_row_values_for_selected_fields",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


def get_row_values_for_fields(lyr, table, fields, select_field, value):
#    msg("--------------------------")
#    msg("Executing get_row_values_for_selected_fields...")
    start_time = time.clock()

    try:
        debug = 0
        value_list = []
        type_list = []
        length_list = []
        check_list = list(fields)
        if select_field is not None:
            check_list.append(select_field)
        return_error = True

        if lyr:
            searchInput = lyr
        else:
            searchInput = get_full_path_from_layer(table)

        if arcpy.Exists(searchInput):
            real_fields = arcpy.ListFields(searchInput)
            if value == "no_expression":
                expression = None
            else:
                expression = arcpy.AddFieldDelimiters(table, select_field) + " = '" + str(value) + "'"

            if check_fields(searchInput, check_list, return_error, 0) == 0:
                with arcpy.da.SearchCursor(searchInput, fields, expression) as cursor:
                    for row in cursor:
                        i = 0
                        for field in fields:
                            value_list.append(row[i])

                            # for real_field in real_fields:
                            #     if real_field.name == field:
                            #         type_list.append(real_field.type)
                            #         length_list.append(real_field.length)
                            #         break
                            i += 1

        msg_prefix = "Function get_row_values_for_selected_fields completed successfully."
        failed = False

        return value_list

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "get_row_values_for_selected_fields",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


                msg(msg_body)


def set_row_values_for_field(lyr, table, field, value, debug):
    if debug == 1:
        msg("--------------------------")
        msg("Executing set_row_values_for_field...")

    start_time = time.clock()

    return_error = True

    try:
        if lyr:
            searchInput = lyr
        else:
            searchInput = get_full_path_from_layer(table)

        if arcpy.Exists(searchInput):
            real_fields = arcpy.ListFields(searchInput)

            if check_fields(searchInput, [field], return_error, 0) == 0:
                with arcpy.da.UpdateCursor(searchInput, field) as u_cursor:
                    for u_row in u_cursor:
                        u_row[0] = value
                        u_cursor.updateRow(u_row)

        msg_prefix = "Function set_row_values_for_field completed successfully."
        failed = False

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "set_row_values_for_field",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)



def get_extent_area(local_ws, local_features):

#    msg("--------------------------")
#    msg("Executing get_extent_area...")
    start_time = time.clock()

    try:
        debug = 0
        if in_memory_switch:
            temp_hull = "in_memory/temp_hull"
        else:
            temp_hull = os.path.join(local_ws, "temp_hull")
            if arcpy.Exists(temp_hull):
                arcpy.Delete_management(temp_hull)

        desc = arcpy.Describe(local_features)
        extent = desc.extent
        array = arcpy.Array()
        # Create the bounding box
        array.add(extent.lowerLeft)
        array.add(extent.lowerRight)
        array.add(extent.upperRight)
        array.add(extent.upperLeft)
        # ensure the polygon is closed
        array.add(extent.lowerLeft)
        # Create the polygon object
        polygon = arcpy.Polygon(array)
        array.removeAll()
        # save to disk
        arcpy.CopyFeatures_management(polygon, temp_hull)
        arcpy.AddField_management(temp_hull, "Shape_Area", "DOUBLE")
        exp = "!shape.area!"
        arcpy.CalculateField_management(temp_hull, "Shape_Area", exp, "PYTHON_9.3")

        del polygon

        msg_prefix = "Function get_extent_area function completed successfully."
        failed = False

        return get_row_values_for_fields(None, temp_hull, ["Shape_Area"], None, "no_expression")[0]

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "get_extent_area",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


def get_shape_area_field(in_feature_class, debug):
    if debug == 1:
        msg("--------------------------")
        msg("Executing get_shape_area_field...")

    start_time = time.clock()

    try:
        shape_area_field = None

        real_fields = arcpy.ListFields(in_feature_class)

        for f in real_fields:
            if f.name.lower() == "shape_area":
                shape_area_field = f.name

        msg_prefix = "get_shape_area_field completed successfully."
        failed = False
        return shape_area_field

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "get_shape_area_field",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)





def check_max_number_of_split(ws, features, id_field, area_field, my_area_field, panel_size, max_split, debug):

    if debug == 1:
        msg("--------------------------")
        msg("Executing check_max_number_of_split...")

    start_time = time.clock()

    try:
        check = True

        # check feature type
        input_type = arcpy.Describe(features).shapetype
        units = arcpy.Describe(features).spatialReference.linearUnitName

        local_area_field = area_field

        # go to polygon to get SHAPE_Area
        if input_type == "MultiPatch":
            calculate_footprint_area(ws, features, area_field, my_area_field, id_field, debug)
            local_area_field = my_area_field

        # check for SHAPE_Area attribute
        if check_fields(features, [local_area_field], True, debug) == 0:
            unique_field_values = unique_values(features, local_area_field)

            list_len = len(unique_field_values)
            largest_area = unique_field_values[list_len - 1]

            if "Foot" in units:
                largest_area *= 0.092903

            if "Feet" in units:
                largest_area *= 0.092903

            number_of_panels = largest_area / (panel_size * panel_size)

            if number_of_panels > max_split:
                check = False

        msg_prefix = "Function check_max_number_of_split completed successfully."
        failed = False

        return check

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "check_max_number_of_split",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


def calculate_footprint_area(ws, features, area_field, my_area_field, join_field, debug):
    if debug == 1:
        msg("--------------------------")
        msg("Executing calculate_footprint_area...")

    start_time = time.clock()

    try:
        temp_footprint = os.path.join(ws, "temp_footprint")
        if arcpy.Exists(temp_footprint):
            arcpy.Delete_management(temp_footprint)

        arcpy.MultiPatchFootprint_3d(features, temp_footprint)
        delete_add_field(temp_footprint, my_area_field, "DOUBLE")
        arcpy.CalculateField_management(temp_footprint, my_area_field, "!" + area_field + "!", "PYTHON_9.3", None)

        fieldList = [my_area_field]

        delete_fields(features, fieldList)

        arcpy.JoinField_management(features, join_field, temp_footprint, join_field, fieldList)

        msg_prefix = "Function calculate_footprint_area completed successfully."
        failed = False

    except:
        line, filename, synerror = trace()
        failed = True
        msg_prefix = ""
        raise FunctionError(
            {
                "function": "calculate_footprint_area",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc": str(arcpy.GetMessages(2))
            }
        )

    finally:
        end_time = time.clock()
        msg_body = create_msg_body(msg_prefix, start_time, end_time)
        if failed:
            msg(msg_body, ERROR)
        else:
            if debug == 1:
                msg(msg_body)


def set_data_paths_for_packaging(data_dir, gdb, fc, model_dir, pf, rule_dir, rule, layer_dir, lf):
    try:
        scriptPath = sys.path[0]
        thisFolder = os.path.dirname(scriptPath)

        dataPath = os.path.join(thisFolder, data_dir)
        one_fc = os.path.join(dataPath, gdb, fc)

        modelPath = os.path.join(thisFolder, model_dir)
        one_modelfile = os.path.join(modelPath, pf)

        rulePath = os.path.join(thisFolder, rule_dir)
        one_rulefile = os.path.join(rulePath, rule)

        layerPath = os.path.join(thisFolder, layer_dir)
        one_layerfile = os.path.join(layerPath, lf)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])


def rename_file_extension(data_dir, from_extentsion, to_extension):
    try:
        files = os.listdir(data_dir)
        for filename in files:
            infilename = os.path.join(data_dir, filename)
            if os.path.isfile(infilename):
                file_ext = os.path.splitext(filename)[1]
                if from_extentsion == file_ext:
                    newfile = infilename.replace(from_extentsion, to_extension)
                    os.rename(infilename, newfile)

    except arcpy.ExecuteWarning:
        print((arcpy.GetMessages(1)))
        arcpy.AddWarning(arcpy.GetMessages(1))

    except arcpy.ExecuteError:
        print((arcpy.GetMessages(2)))
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        #
        e = sys.exc_info()[1]
        print((e.args[0]))
        arcpy.AddError(e.args[0])