library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity test_axi_mm is
    port(clk:     in  std_logic;
         awready: out std_logic;
         awvalid: in  std_logic;
         awaddr:  in  std_logic_vector(3 downto 0);
         awprot:  in  std_logic_vector(2 downto 0);
         wready:  out std_logic;
         wvalid:  in  std_logic;
         wdata:   in  std_logic_vector(31 downto 0);
         wstrb:   in  std_logic_vector(3 downto 0);
         bready:  in  std_logic;
         bvalid:  out std_logic;
         bresp:   out std_logic_vector(1 downto 0);
         arready: out std_logic;
         arvalid: in  std_logic;
         araddr:  in  std_logic_vector(3 downto 0);
         arprot:  in  std_logic_vector(2 downto 0);
         rready:  in  std_logic;
         rvalid:  out std_logic;
         rdata:   out std_logic_vector(31 downto 0);
         rresp:   out std_logic_vector(1 downto 0));
end entity;

architecture rtl of test_axi_mm is
    type registers_t is array (0 to 3) of std_logic_vector(31 downto 0);
    signal registers:  registers_t := (others => (others => '0'));
    signal write_ready: std_logic;
    signal read_ready:  std_logic;
    signal bvalid_q:    std_logic := '0';
    signal rvalid_q:    std_logic := '0';
begin
    -- AWREADY and WREADY wait for both AWVALID and WVALID
    write_ready <= awvalid and wvalid and not bvalid_q;
    read_ready  <= not rvalid_q;

    awready <= write_ready;
    wready  <= write_ready;
    bvalid  <= bvalid_q;
    bresp   <= "00";
    arready <= read_ready;
    rvalid  <= rvalid_q;
    rresp   <= "00";

    process(clk)
    begin
        if rising_edge(clk) then
            if write_ready = '1' then
                for byte in 0 to 3 loop
                    if wstrb(byte) = '1' then
                        registers(to_integer(unsigned(awaddr(3 downto 2))))(8 * byte + 7 downto 8 * byte) <= wdata(8 * byte + 7 downto 8 * byte);
                    end if;
                end loop;
                bvalid_q <= '1';
            elsif bready = '1' then
                bvalid_q <= '0';
            end if;

            if arvalid = '1' and read_ready = '1' then
                rdata    <= registers(to_integer(unsigned(araddr(3 downto 2))));
                rvalid_q <= '1';
            elsif rready = '1' then
                rvalid_q <= '0';
            end if;
        end if;
    end process;
end architecture;
