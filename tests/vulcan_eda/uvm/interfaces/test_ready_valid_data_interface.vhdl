library ieee;
use ieee.std_logic_1164.all;

entity test_ready_valid_data_interface is
    port(clk:              in  std_logic;
         upstream_ready:   out std_logic;
         upstream_valid:   in  std_logic;
         upstream_data:    in  std_logic_vector(7 downto 0);
         downstream_ready: in  std_logic;
         downstream_valid: out std_logic;
         downstream_data:  out std_logic_vector(7 downto 0));
end entity;

architecture rtl of test_ready_valid_data_interface is
begin
    upstream_ready   <= downstream_ready;
    downstream_valid <= upstream_valid;
    downstream_data  <= upstream_data;
end architecture;
