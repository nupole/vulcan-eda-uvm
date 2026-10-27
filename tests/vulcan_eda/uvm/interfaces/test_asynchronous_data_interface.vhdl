library ieee;
use ieee.std_logic_1164.all;

entity test_asynchronous_data_interface is
    port(upstream_first:    in  std_logic_vector(7 downto 0);
         upstream_second:   in  std_logic_vector(7 downto 0);
         downstream_first:  out std_logic_vector(7 downto 0);
         downstream_second: out std_logic_vector(7 downto 0));
end entity;

architecture rtl of test_asynchronous_data_interface is
begin
    downstream_first <= upstream_first;
    downstream_second <= upstream_second;
end architecture;
