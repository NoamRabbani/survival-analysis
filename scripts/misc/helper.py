"""
Helper functions that are used by other python modules

Copyright (C) 2019  Noam Rabbani
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
Email: hello@noamrabbani.com
"""

import os

class Helper:
    """ Helper functions.
    """

    def get_directory_paths(project):
        """ Gets the paths to the project's directories.

        Args:
            project: Project for which we are generating the dataset.
        Returns:
            input_paths: Dictionary containing paths of input files.
            output_path: Dictionary containing paths of output files.
        """
        helper_file_path = os.path.dirname(os.path.realpath(__file__))
        project_dir = os.path.join(helper_file_path, "..", "..")
        
        dir_paths = {
            "artifacts": os.path.join(project_dir, "artifacts")
            "cross_issue_data": os.path.join(project_dir, "cross_issue_data")
            "datasets": os.path.join(project_dir, "datasets")
            "figures": os.path.join(project_dir, "figures")
            "logs": os.path.join(project_dir, "logs")
            "plots": os.path.join(project_dir, "plots")
        }
        return dir_paths


if __name__ == "__main__":
    main()


