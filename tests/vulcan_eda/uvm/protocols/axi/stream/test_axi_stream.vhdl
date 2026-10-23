library ieee;
use ieee.std_logic_1164.all;

entity test_axi_stream is
    port(clk:               in  std_logic;
         upstream_tready:   out std_logic;
         upstream_tvalid:   in  std_logic;
         upstream_tdata:    in  std_logic_vector(31 downto 0);
         upstream_tlast:    in  std_logic;
         downstream_tready: in  std_logic;
         downstream_tvalid: out std_logic;
         downstream_tdata:  out std_logic_vector(31 downto 0);
         downstream_tlast:  out std_logic);
end entity;

architecture rtl of test_axi_stream is
begin
    upstream_tready   <= downstream_tready;
    downstream_tvalid <= upstream_tvalid;
    downstream_tdata  <= upstream_tdata;
    downstream_tlast  <= upstream_tlast;
end architecture;
