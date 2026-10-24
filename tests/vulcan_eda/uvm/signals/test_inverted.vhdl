library ieee;
use ieee.std_logic_1164.all;

entity test_inverted is
    port(clk:             in  std_logic;
         ref_bit_in:      in  std_logic;
         ref_bus_in:      in  std_logic_vector(3 downto 0);
         ref_bit_out:     out std_logic;
         ref_bus_out:     out std_logic_vector(3 downto 0);
         bit_n_in:        in  std_logic;
         bus_n_in:        in  std_logic_vector(3 downto 0);
         bit_out:         out std_logic;
         bus_out:         out std_logic_vector(3 downto 0);
         bit_n_out:       out std_logic;
         bus_n_out:       out std_logic_vector(3 downto 0));
end entity;

architecture rtl of test_inverted is
begin
    ref_bit_out <= ref_bit_in;
    ref_bus_out <= ref_bus_in;
    bit_out     <= not bit_n_in;
    bus_out     <= not bus_n_in;
    bit_n_out   <= not ref_bit_in;
    bus_n_out   <= not ref_bus_in;
end architecture;
