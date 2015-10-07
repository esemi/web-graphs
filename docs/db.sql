--
-- Table structure for table `domain`
--
CREATE TABLE IF NOT EXISTS `domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_full` varchar(255) NOT NULL,
  `tld` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_domains_domain` (`domain_full`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

ALTER TABLE `domain` ADD `date_add` DATE NOT NULL;