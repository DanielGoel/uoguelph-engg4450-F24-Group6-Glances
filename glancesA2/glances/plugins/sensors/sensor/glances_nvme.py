import subprocess
from glances.plugins.plugin.model import GlancesPluginModel


class PluginModel(GlancesPluginModel):
    """Glances NVMe plugin for sensors."""

    def __init__(self, args=None, config=None):
        super().__init__(args=args, config=config, stats_init_value=[])
        self.nvme = GlancesGrabNVMe()
        self.display_curse = True

    def update(self):
        stats = self.get_init_value()
        nvme_data = self.nvme.get()
        if nvme_data:
            stats.append({'label': 'NVMe Temp', 'value': nvme_data['temperature'], 'unit': 'C'})
        self.stats = stats
        return self.stats

    def msg_curse(self, args=None, max_width=None):
        """Display NVMe data in the curses interface."""
        ret = []
        if not self.stats or self.is_disabled():
            return ret
        if max_width:
            label_max_width = max_width - 14
        # Display the header
        ret.append(self.curse_add_line('NVMe Stats', "TITLE"))
        # Display the temperature and other details
        for stat in self.stats:
            ret.append(self.curse_new_line())
            ret.append(self.curse_add_line(f'{stat["label"]}', width=label_max_width))
            ret.append(self.curse_add_line(f'{stat["value"]} {stat["unit"]}', align='right'))
        return ret

class GlancesGrabNVMe:
    """Fetch NVMe stats using the smartctl command."""

    def __init__(self):
        pass

    def get(self):
        """Fetch NVMe data and return relevant stats."""
        nvme_data = {}
        try:
            output = subprocess.check_output(
                [r"C:\Program Files\Smartmontools\bin\smartctl.exe", '-a', '/dev/sdc', '-d', 'nvme'],
                universal_newlines=True
            )
            nvme_data = self.parse_nvme_output(output)
        except subprocess.CalledProcessError as e:
            print(f"Error executing smartctl: {e}")
        return nvme_data

    def parse_nvme_output(self, output):
        """Parse the output from smartctl to extract NVMe stats."""
        nvme_data = {}
        for line in output.splitlines():
            if 'Temperature:' in line:
                nvme_data['temperature'] = int(line.split()[-2])
            elif 'Power Cycles:' in line:
                nvme_data['power_cycles'] = int(line.split()[-1])
            elif 'Percentage Used:' in line:
                nvme_data['percentage_used'] = int(line.split()[-1].replace('%', ''))
        return nvme_data
