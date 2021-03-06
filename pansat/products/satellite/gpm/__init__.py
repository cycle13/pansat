"""
pansat.products.satellite.gpm
=============================

This module defines the GPM product class, which is used to represent all
GPM products.
"""
import re
from datetime import datetime
from pathlib import Path

import pansat.download.providers as providers
from pansat.products.product import Product


class NoAvailableProviderError(Exception):
    """
    Exception indicating that no suitable provider could be found for
    a product.
    """


class GPMProduct(Product):
    """
    """

    def __init__(self, name):
        self.name = name
        self.level, self.product_name = name.split("_")
        self.filename_regexp = re.compile(
            rf"{self.level}\.GPM\.{self.product_name}\.([\w-]*)\.(\d{{8}})-"
            r"S(\d{6})-E(\d{6})\.(\w*)\.(\w*).HDF5"
        )

    @property
    def variables(self):
        return []

    def matches(self, filename):
        """
        Determines whether a given filename matches the pattern used for
        the product.

        Args:
            filename(``str``): The filename

        Return:
            True if the filename matches the product, False otherwise.
        """
        return self.filename_regexp.match(filename)

    def filename_to_date(self, filename):
        """
        Extract timestamp from filename.

        Args:
            filename(``str``): Filename of a CloudSat product.

        Returns:
            ``datetime`` object representing the timestamp of the
            filename.
        """
        path = Path(filename)
        match = self.filename_regexp.match(path.name)
        date_string = match.group(2) + match.group(3)
        date = datetime.strptime(date_string, "%Y%m%d%H%M%S")
        return date

    def _get_provider(self):
        """ Find a provider that provides the product. """
        available_providers = [
            p
            for p in providers.ALL_PROVIDERS
            if str(self) in p.get_available_products()
        ]
        if not available_providers:
            raise NoAvailableProviderError(
                f"Could not find a provider for the" f" product {self.name}."
            )
        return available_providers[0]

    @property
    def default_destination(self):
        """
        The default destination for CloudSat product is
        ``CloudSat/<product_name>``>
        """
        return Path("GPM") / Path(self.name)

    def __str__(self):
        """ The full product name. """
        return "GPM_" + self.name

    def download(self, start_time, end_time, destination=None, provider=None):
        """
        Download data product for given time range.

        Args:
            start_time(``datetime``): ``datetime`` object defining the start
                 date of the time range.
            end_time(``datetime``): ``datetime`` object defining the end date
                 of the of the time range.
            destination(``str`` or ``pathlib.Path``): The destination where to
                 store the output data.
        """

        if not provider:
            provider = self._get_provider()

        if not destination:
            destination = self.default_destination
        else:
            destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        provider = provider(self)

        return provider.download(start_time, end_time, destination)

    def open(self, filename):
        """
        Open file as xarray dataset.

        Args:
            filename(``pathlib.Path`` or ``str``): The CloudSat file to open.
        """
        pass


l2a_dpr = GPMProduct("2A_DPR")
l2b_dpr_gmi = GPMProduct("2B_DPRGMI")
l2a_gprof_gmi = GPMProduct("2A_GMI")
