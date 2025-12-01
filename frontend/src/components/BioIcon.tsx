import React from 'react';
import { FaDna, FaMicroscope, FaVial, FaChartBar, FaUpload, FaDownload, FaFlask, FaDatabase, FaFileAlt } from 'react-icons/fa';
import './BioIcon.css';

interface BioIconProps {
  type: 'dna' | 'microscope' | 'vial' | 'chart' | 'upload' | 'download' | 'flask' | 'database' | 'file';
  size?: 'small' | 'medium' | 'large';
  className?: string;
  spin?: boolean;
  pulse?: boolean;
  is3d?: boolean;
}

const BioIcon: React.FC<BioIconProps> = ({
  type,
  size = 'medium',
  className = '',
  spin = false,
  pulse = false,
  is3d = false
}) => {
  const baseClasses = `bio-icon ${size} ${spin ? 'spin' : ''} ${pulse ? 'pulse' : ''}`;
  const iconClasses = is3d
    ? `${baseClasses} bio-icon-3d ${className}`
    : `${baseClasses} ${className}`;

  const iconSize = size === 'small' ? '1em' : size === 'large' ? '1.5em' : '1.2em';

  const getIcon = () => {
    if (is3d) {
      // For 3D effect, we'll render the icon with front/back/side elements
      let iconElement;
      switch (type) {
        case 'dna':
          iconElement = <FaDna className="icon-front" size={iconSize} />;
          break;
        case 'microscope':
          iconElement = <FaMicroscope className="icon-front" size={iconSize} />;
          break;
        case 'vial':
          iconElement = <FaVial className="icon-front" size={iconSize} />;
          break;
        case 'chart':
          iconElement = <FaChartBar className="icon-front" size={iconSize} />;
          break;
        case 'upload':
          iconElement = <FaUpload className="icon-front" size={iconSize} />;
          break;
        case 'download':
          iconElement = <FaDownload className="icon-front" size={iconSize} />;
          break;
        case 'flask':
          iconElement = <FaFlask className="icon-front" size={iconSize} />;
          break;
        case 'database':
          iconElement = <FaDatabase className="icon-front" size={iconSize} />;
          break;
        case 'file':
          iconElement = <FaFileAlt className="icon-front" size={iconSize} />;
          break;
        default:
          iconElement = <FaDna className="icon-front" size={iconSize} />;
      }

      return (
        <div className={iconClasses} data-type={type}>
          {iconElement}
          <div className="icon-back">{iconElement}</div>
          <div className="icon-side"></div>
        </div>
      );
    } else {
      // For regular (non-3D) icon
      const iconProps = {
        className: iconClasses,
        size: iconSize,
        'data-type': type
      };

      switch (type) {
        case 'dna':
          return <FaDna {...iconProps} />;
        case 'microscope':
          return <FaMicroscope {...iconProps} />;
        case 'vial':
          return <FaVial {...iconProps} />;
        case 'chart':
          return <FaChartBar {...iconProps} />;
        case 'upload':
          return <FaUpload {...iconProps} />;
        case 'download':
          return <FaDownload {...iconProps} />;
        case 'flask':
          return <FaFlask {...iconProps} />;
        case 'database':
          return <FaDatabase {...iconProps} />;
        case 'file':
          return <FaFileAlt {...iconProps} />;
        default:
          return <FaDna {...iconProps} />;
      }
    }
  };

  return getIcon();
};

export default BioIcon;