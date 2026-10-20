library ieee;
use ieee.std_logic_1164.all;

entity test_data_interface is
    port(clk:             in  std_logic;
         upstream_data:   in  std_logic_vector(7 downto 0);
         downstream_data: out std_logic_vector(7 downto 0));
end entity;

architecture rtl of test_data_interface is
begin
    process(clk) begin
        if rising_edge(clk) then
            downstream_data <= upstream_data;
        end if;
    end process;
end architecture;
