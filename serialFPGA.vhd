-- synthesis library my_lib
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

package serialFPGA is
	component simpleUSB is
		generic (g_noBytes : integer:=1);
		port 	(	i_clk				: in std_logic;
					i_reset			: in std_logic;
					i_fromSystem 	: in std_logic_vector(g_noBytes*8-1 downto 0);
					i_fromUSB		: in std_logic;
					o_toSystem		: out std_logic_vector(g_noBytes*8-1 downto 0);
					o_toUSB			: out std_logic;
					o_valid			: out std_logic);
	end component;
end package;
