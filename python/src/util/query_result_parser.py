# This class implements a simple key-based counter, often used
# for data exploration and wrangling.
# Chris Joakim, Microsoft

import json
import logging
import re
import traceback


class QueryResultParser:
    """
    Instances of this class parse the results of Azure PostgreSQL
    and Apache AGE queries.
    """

    def __init__(self):
        pass

    def parse(self, query_result: tuple) -> list:
        """
        psycopg cursor.execute() returns a tuple of tuples, which this method
        parses into a list of parsed objects.
        
        The Apache AGE query result tuples contain odd string that contain string
        values like '::vertex' and '::edge' that are removed here then parsed into
        JSON objects.

        If the length of the parsed values list is just 1, then the single value
        is returned instead of the list.
        """
        try:
            if isinstance(query_result, tuple):
                row_values = list()
                for elem_idx, elem in enumerate(query_result):
                    #print("QueryResultParser#parse - elem: {} {} {}".format(elem_idx, str(type(elem)), elem))
                    if isinstance(elem, str):
                        scrubbed = self.scrub_colonpair_str_values(elem)
                        if self.is_json_string(scrubbed):
                            try:
                                row_values.append(json.loads(scrubbed))
                            except Exception as e:
                                logging.error("QueryResultParser#parse json parse exception: {} {}".format(
                                    str(e), elem))
                                row_values.append(scrubbed)
                        else:
                            row_values.append(scrubbed)
                    else:
                        row_values.append(elem)

                if len(row_values) == 1:
                    return row_values[0]
                else:
                    return row_values
        except Exception as e:
            logging.error("QueryResultParser - exception:", str(e))
            logging.error(traceback.format_exc())
        return None

    def scrub_colonpair_str_values(self, s):
        """
        Use the re standard library to remove the '::vertex' and '::edge' strings.
        """
        if '::' in s:
            s1 = re.sub('::vertex', '', s)
            return re.sub('::edge', '', s1).strip()
        else:
            return s.strip()
        
    def is_json_string(self, s):
        """
        Return a boolean indicating whether the given string is a JSON string.
        """
        if isinstance(s, str):
            if s.startswith("{") and s.endswith("}"):
                return True
            if s.startswith("[") and s.endswith("]"):
                return True
        return False
