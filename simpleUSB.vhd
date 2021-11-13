--Simple USB
--The key goal of this is to offload all complexity to either the python module to control it,
-- or to the modules in the USB to serial that this interfaces with!
--Really, it is just a simple serial to parallel converter that can also deal with the stop and start bits
-- of a serial line!
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;


entity simpleUSB is
	generic (g_noBytes : integer:=1);
	port 	(	i_clk				: in std_logic;
				i_reset			: in std_logic;
				i_fromSystem 	: in std_logic_vector(g_noBytes*8-1 downto 0);
			   i_fromUSB		: in std_logic;
				o_toSystem		: out std_logic_vector(g_noBytes*8-1 downto 0);
				o_toUSB			: out std_logic;
				o_valid			: out std_logic);
end simpleUSB;



architecture arch of simpleUSB is

	
	signal r_nowByte 		: integer range 0 to g_noBytes-1 :=0;
	signal r_nowBit		: integer range 0 to 9:=0;
	signal r_fromSysBuff	: std_logic_vector(g_noBytes*8-1 downto 0);
	signal r_toSysBuff	: std_logic_vector(g_noBytes*8-1 downto 0);
	signal r_counter		: unsigned (1 downto 0); --Extremely crude synchronisation!
	signal r_armStart		: std_logic:='0';
	signal r_toTarget 	: integer range 0 to g_noBytes*8:=0;
	
begin
	
	ONLY: process (i_clk, i_reset, i_fromSystem, i_fromUSB)
	begin
		if (i_reset = '1') then
			r_nowByte <= 0;
			r_nowBit <= 0;
			
			r_counter <= to_unsigned(0,2);
			r_armStart <= '0';
			
			o_valid <= '0';
			o_toSystem <= (others => '0');
			o_toUSB <= '1';
			
			r_fromSysBuff <= (others => '0');
			r_toSysBuff <= ( others => '0');
			
			r_toTarget <= 0;
			
		elsif rising_edge(i_clk) then
			case r_nowBit is
				when 0 =>
					if (i_fromUSB = '0') then
						if (r_armStart = '0') then
							r_counter <= to_unsigned(0,2);
							r_armStart <= '1';
							r_fromSysBuff <= i_fromSystem;
							o_valid <= '0';
						else
							if (r_counter= to_unsigned(3,2)) then
								r_nowBit <= 1;
								r_armStart <= '0';
							end if;
						end if;
						r_counter <= r_counter + to_unsigned(1,2);
						o_toUSB <= '0';
					else
						o_toUSB <= '1';
					end if;
					r_toTarget <= r_nowByte*8 + r_nowBit;
					
				when 9 =>
					r_counter <= r_counter + to_unsigned(1,2);
					o_toUSB <= '1';
					if (r_counter = to_unsigned(3,2) ) then
						r_nowBit <= 0;
						r_counter <= r_counter + to_unsigned(1,2);
						if (r_nowByte = g_noBytes-1) then
							r_nowByte <= 0; --These only become accessible on the next cycle!
							o_toSystem <= r_toSysBuff;
							o_valid <= '1';
						else
							r_nowByte <= r_nowByte + 1;						
						end if;
					end if;
					
				when others =>
					r_counter <= r_counter + to_unsigned(1,2);
					o_toUSB <= r_fromSysBuff(r_toTarget);

					--Don't need a when others statement
					case r_counter is
						when to_unsigned(1,2) =>
							r_toSysBuff(r_nowByte*8 + r_nowBit - 1) <= i_fromUSB;
						when to_unsigned(3,2) =>
							r_nowBit <= r_nowBit + 1;
							r_toTarget <= r_nowByte*8 + r_nowBit;
						when others =>
							null;
					end case;
					
			end case;
		end if;
	end process ONLY;
	
	
end arch;